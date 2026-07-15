import sys
import os
import gspread

# Thêm đường dẫn để import core
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.config import settings
from etl.loader import SheetsLoader

def migrate():
    print("Bắt đầu quy hoạch lại Database_Full (Gộp Năng Lực và Mục Tiêu thành 1 cột Điểm số)...")
    gc = gspread.service_account(filename=settings.GOOGLE_APPLICATION_CREDENTIALS)
    loader = SheetsLoader(gc, settings.GOOGLE_SHEET_URL)
    
    rows = loader.get_all_database_records()
    if not rows:
        print("Sheet trống.")
        return
        
    new_rows = []
    for i, row in enumerate(rows):
        if i == 0:
            new_rows.append(["Task ID", "Tên Task", "Trạng thái", "Ngày hoàn thành", "Điểm số"])
            continue
            
        nang_luc = 0.0
        if len(row) > 4 and row[4]:
            try: nang_luc = float(row[4])
            except: pass
            
        muc_tieu = 0.0
        if len(row) > 5 and row[5]:
            try: muc_tieu = float(row[5])
            except: pass
            
        total = nang_luc + muc_tieu
        
        # New row có 5 cột
        new_row = [
            row[0] if len(row) > 0 else "",
            row[1] if len(row) > 1 else "",
            row[2] if len(row) > 2 else "",
            row[3] if len(row) > 3 else "",
            total
        ]
        new_rows.append(new_row)
        
    loader.bulk_update_database(new_rows)
    print("Quy hoạch xong Database_Full!")

if __name__ == "__main__":
    migrate()
