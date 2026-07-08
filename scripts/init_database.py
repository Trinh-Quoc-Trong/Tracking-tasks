import sys
import os
import requests
import gspread
from datetime import datetime

# Đảm bảo có thể import module core
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.config import settings

def format_timestamp(ts_str):
    if not ts_str:
        return ""
    try:
        # ClickUp timestamps are in milliseconds
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

def main():
    print("1. Kết nối Google Sheets...")
    gc = gspread.service_account(filename=settings.GOOGLE_APPLICATION_CREDENTIALS)
    spreadsheet = gc.open_by_url(settings.GOOGLE_SHEET_URL)
    
    # Tạo sheet Database (nếu chưa có)
    try:
        db_sheet = spreadsheet.worksheet('Database_Full')
        print("-> Sheet 'Database_Full' đã tồn tại, đang dọn dẹp dữ liệu cũ...")
        db_sheet.clear()
    except gspread.exceptions.WorksheetNotFound:
        print("-> Đang tạo Sheet mới 'Database_Full'...")
        db_sheet = spreadsheet.add_worksheet(title='Database_Full', rows="5000", cols="10")
        
    print("2. Đang quét toàn bộ các task trong Workspace từ ClickUp (Pagination)...")
    headers = {"Authorization": settings.CLICKUP_API_TOKEN}
    url = f"https://api.clickup.com/api/v2/team/{settings.CLICKUP_TEAM_ID}/task"
    
    all_tasks = []
    page = 0
    while True:
        params = {
            "subtasks": "true",
            "include_closed": "true",
            "page": page
        }
        resp = requests.get(url, headers=headers, params=params)
        if resp.status_code != 200:
            print(f"Lỗi gọi API: {resp.status_code} - {resp.text}")
            break
            
        tasks = resp.json().get('tasks', [])
        if not tasks:
            break
        all_tasks.extend(tasks)
        page += 1
        if len(tasks) < 100:
            break
            
    print(f"-> Đã kéo về tổng cộng {len(all_tasks)} tasks.")
    
    print("3. Đang xử lý và bóc tách dữ liệu...")
    # Header của Database
    table_data = [
        ["Task ID", "Tên Task", "Trạng thái", "Ngày hoàn thành (End Time)", "Hiệu suất với năng lực", "Hiệu xuất với mục tiêu"]
    ]
    
    for task in all_tasks:
        status_info = task.get("status", {})
        status_name = status_info.get("status", "")
        status_type = status_info.get("type", "")
        
        # Chỉ lấy các task đã đóng hoàn toàn (type: closed)
        if status_type.lower() != "closed":
            continue
            
        task_id = task.get("id")
        name = task.get("name")
        end_time = format_timestamp(task.get("date_closed"))
        
        custom_fields = task.get("custom_fields", [])
        
        score_nang_luc = extract_field(custom_fields, ["năng lực"])
        score_muc_tieu = extract_field(custom_fields, ["mục tiêu"])
        
        row = [task_id, name, status_name, end_time, score_nang_luc, score_muc_tieu]
        table_data.append(row)
        
    print("4. Đang ghi dữ liệu lên Google Sheets...")
    # Push 1 lần duy nhất cho toàn bộ mảng dữ liệu (Cực kỳ tối ưu tốc độ)
    db_sheet.update(values=table_data, range_name='A1')
    
    print("✅ HOÀN TẤT! Toàn bộ lịch sử Task đã được đẩy lên Sheet 'Database_Full'.")

if __name__ == "__main__":
    main()
