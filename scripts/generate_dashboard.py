import sys
import os
import gspread

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.config import settings
from etl.transformer import DataTransformer
from etl.loader import SheetsLoader

def main():
    print("1. Đọc dữ liệu từ Database_Full...")
    gc = gspread.service_account(filename=settings.GOOGLE_APPLICATION_CREDENTIALS)
    loader = SheetsLoader(gc, settings.GOOGLE_SHEET_URL)
    
    all_data = loader.get_all_database_records()
    if not all_data or len(all_data) <= 1:
        print("Không có dữ liệu trong Database để vẽ đồ thị.")
        return

    print("2. Đang xử lý dữ liệu (Lọc 30 ngày & Tính trung bình)...")
    # Bỏ qua dòng Header
    data_rows = all_data[1:] 
    
    transformer = DataTransformer()
    recent_tasks = transformer.filter_last_30_days(data_rows)
    daily_averages = transformer.calculate_daily_averages(recent_tasks)

    print("3. Đang ghi lên Sheet 'Dashboard_30_Days' và vẽ biểu đồ...")
    loader.update_dashboard_view(daily_averages)
    loader.draw_chart()
    
    print("✅ Đã vẽ xong đồ thị trực tiếp trên Google Sheets!")

if __name__ == "__main__":
    main()
