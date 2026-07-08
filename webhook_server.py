import sys
import os
from fastapi import FastAPI, Request, BackgroundTasks
import json
import requests
import gspread
from datetime import datetime

# Đảm bảo import được module core
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from core.config import settings

# Import hàm vẽ dashboard để chạy lại mỗi khi có task mới
from scripts.generate_dashboard import main as generate_dashboard_main

app = FastAPI(title="ClickUp Webhook Receiver")

def fetch_task_details(task_id: str):
    """Gọi lại API của ClickUp để lấy toàn bộ thông tin chi tiết của task (bao gồm Custom Fields)"""
    url = f"https://api.clickup.com/api/v2/task/{task_id}"
    headers = {"Authorization": settings.CLICKUP_API_TOKEN}
    params = {"custom_task_ids": "true", "team_id": settings.CLICKUP_TEAM_ID}
    resp = requests.get(url, headers=headers, params=params)
    if resp.status_code == 200:
        return resp.json()
    return None

def format_timestamp(ts_str):
    if not ts_str:
        return ""
    try:
        ts = int(ts_str) / 1000.0
        return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return ""

def extract_field(custom_fields, target_keywords):
    for field in custom_fields:
        name = field.get('name', '').lower()
        if any(kw in name for kw in target_keywords):
            return field.get('value')
    return ""

def process_closed_task(task_id: str):
    """Hàm chạy ngầm (Background): Lấy chi tiết Task -> Đẩy vào Database -> Cập nhật Dashboard"""
    print(f"\n🔄 BẮT ĐẦU XỬ LÝ TASK VỪA ĐÓNG: {task_id}")
    task_data = fetch_task_details(task_id)
    if not task_data:
        print(f"❌ Không lấy được dữ liệu chi tiết cho task {task_id}")
        return
        
    name = task_data.get("name")
    status_name = task_data.get("status", {}).get("status", "")
    end_time = format_timestamp(task_data.get("date_closed"))
    
    custom_fields = task_data.get("custom_fields", [])
    score_nang_luc = extract_field(custom_fields, ["năng lực"])
    score_muc_tieu = extract_field(custom_fields, ["mục tiêu"])
    
    row = [task_id, name, status_name, end_time, score_nang_luc, score_muc_tieu]
    
    print(f"-> Đã bóc tách dữ liệu: {name} (Năng lực: {score_nang_luc}, Mục tiêu: {score_muc_tieu})")
    
    try:
        print("-> Đang ghi thêm dòng mới vào Sheet Database_Full...")
        gc = gspread.service_account(filename=settings.GOOGLE_APPLICATION_CREDENTIALS)
        spreadsheet = gc.open_by_url(settings.GOOGLE_SHEET_URL)
        db_sheet = spreadsheet.worksheet('Database_Full')
        db_sheet.append_row(row)
        
        print("-> Đang cập nhật lại Đồ thị Dashboard...")
        # Gọi lại kịch bản vẽ đồ thị
        generate_dashboard_main()
        print("✅ TOÀN BỘ QUY TRÌNH WEBHOOK ĐÃ HOÀN TẤT THÀNH CÔNG TỰ ĐỘNG!\n")
    except Exception as e:
        print(f"❌ Lỗi trong quá trình cập nhật Sheets: {e}")

@app.get("/")
def read_root():
    return {"message": "Webhook Server đang hoạt động!"}

@app.post("/clickup-webhook")
async def receive_webhook(request: Request, background_tasks: BackgroundTasks):
    """Endpoint này sẽ được ClickUp gọi tới khi có sự kiện."""
    payload = await request.json()
    
    # Lọc lịch sử để kiểm tra xem có phải task vừa chuyển sang trạng thái "Closed" không
    history_items = payload.get('history_items', [])
    if history_items:
        item = history_items[0]
        if item.get("field") == "status":
            after_status = item.get("after", {})
            # Kiểm tra xem trạng thái mới có mang thuộc tính "closed" không
            if after_status.get("type") == "closed":
                task_id = payload.get('task_id')
                print(f"🔔 Tín hiệu: Task {task_id} vừa được đánh dấu hoàn thành!")
                
                # Giao việc xử lý cho BackgroundTask để trả lời 200 OK cho ClickUp ngay lập tức (Rất quan trọng!)
                background_tasks.add_task(process_closed_task, task_id)
                return {"status": "processing_closed_task", "task_id": task_id}
                
    # Bỏ qua các tín hiệu không quan trọng khác (như mở lại task, đổi tên, v.v...)
    return {"status": "ignored"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("webhook_server:app", host="0.0.0.0", port=8000, reload=True)
