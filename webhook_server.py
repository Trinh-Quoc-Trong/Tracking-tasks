import sys
import os
from fastapi import FastAPI, Request, BackgroundTasks
import gspread

# Đảm bảo import được module core
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from core.config import settings

# Import ETL modules chuẩn
from etl.extractor import ClickUpExtractor
from etl.transformer import DataTransformer
from etl.loader import SheetsLoader
from scripts.generate_dashboard import main as generate_dashboard_main

app = FastAPI(title="ClickUp Webhook Receiver")

def process_closed_task(task_id: str):
    """Hàm chạy ngầm (Background): Lấy chi tiết Task -> Đẩy vào Database -> Cập nhật Dashboard"""
    print(f"\n🔄 BẮT ĐẦU XỬ LÝ TASK VỪA ĐÓNG: {task_id}")
    
    # 1. EXTRACT
    extractor = ClickUpExtractor(settings.CLICKUP_API_TOKEN, settings.CLICKUP_TEAM_ID)
    try:
        task_data = extractor.fetch_task_details(task_id)
    except Exception as e:
        print(f"❌ Không lấy được dữ liệu chi tiết cho task {task_id}: {e}")
        return
        
    # Bỏ qua nếu đây là Subtask (có chứa parent ID)
    if task_data.get("parent"):
        print(f"⏭️ Bỏ qua task {task_id} vì đây là một Subtask.")
        return
        
    # 2. TRANSFORM
    transformer = DataTransformer()
    row = transformer.format_task_to_row(task_data)
    
    print(f"-> Đã bóc tách dữ liệu: {row[1]} (Điểm số: {row[4]})")
    
    # 3. LOAD
    try:
        print("-> Đang ghi thêm dòng mới vào Sheet Database_Full...")
        gc = gspread.service_account(filename=settings.GOOGLE_APPLICATION_CREDENTIALS)
        loader = SheetsLoader(gc, settings.GOOGLE_SHEET_URL)
        
        loader.append_new_task(row)
        
        print("-> Đang cập nhật lại Đồ thị Dashboard...")
        # Gọi lại kịch bản vẽ đồ thị chuẩn
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
    
    history_items = payload.get('history_items', [])
    if history_items:
        item = history_items[0]
        if item.get("field") == "status":
            after_status = item.get("after", {})
            if after_status.get("type") == "closed":
                task_id = payload.get('task_id')
                print(f"🔔 Tín hiệu: Task {task_id} vừa được đánh dấu hoàn thành!")
                
                # Chạy ngầm tiến trình ETL
                background_tasks.add_task(process_closed_task, task_id)
                return {"status": "processing_closed_task", "task_id": task_id}
                
    return {"status": "ignored"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("webhook_server:app", host="0.0.0.0", port=8000, reload=True)
