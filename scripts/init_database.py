import sys
import os
import gspread

# Cấu hình đường dẫn
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.config import settings
from etl.extractor import ClickUpExtractor
from etl.transformer import DataTransformer
from etl.loader import SheetsLoader

def main():
    print("1. Kết nối Google Sheets...")
    gc = gspread.service_account(filename=settings.GOOGLE_APPLICATION_CREDENTIALS)
    loader = SheetsLoader(gc, settings.GOOGLE_SHEET_URL)
    
    print("2. Đang quét toàn bộ các task trong Workspace từ ClickUp (Có phân trang)...")
    extractor = ClickUpExtractor(settings.CLICKUP_API_TOKEN, settings.CLICKUP_TEAM_ID)
    # Lấy cả task mở và đóng để sau này Transformer lọc
    all_tasks = extractor.fetch_all_workspace_tasks(include_closed=True)
    print(f"-> Đã kéo về tổng cộng {len(all_tasks)} tasks.")
    
    print("3. Đang xử lý và bóc tách dữ liệu...")
    transformer = DataTransformer()
    
    table_data = [
        ["Task ID", "Tên Task", "Trạng thái", "Ngày hoàn thành (End Time)", "Hiệu suất với năng lực", "Hiệu xuất với mục tiêu"]
    ]
    
    for task in all_tasks:
        # Chỉ lấy task đã đóng hoàn toàn (type: closed)
        status_info = task.get("status", {})
        if status_info.get("type", "").lower() != "closed":
            continue
            
        row = transformer.format_task_to_row(task)
        table_data.append(row)
        
    print("4. Đang ghi đè toàn bộ dữ liệu lên Google Sheets (Sheet: Database_Full)...")
    loader.bulk_update_database(table_data)
    
    print("✅ HOÀN TẤT! Toàn bộ lịch sử Task đã được chuẩn hóa và đẩy lên Database_Full.")

if __name__ == "__main__":
    main()
