import sys
import os
import gspread

# Đảm bảo import được module core
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.config import settings
from etl.transformer import DataTransformer

def main():
    gc = gspread.service_account(filename=settings.GOOGLE_APPLICATION_CREDENTIALS)
    spreadsheet = gc.open_by_url(settings.GOOGLE_SHEET_URL)
    
    print("1. Đọc dữ liệu từ Database_Full...")
    try:
        db_sheet = spreadsheet.worksheet('Database_Full')
    except gspread.exceptions.WorksheetNotFound:
        print("Lỗi: Không tìm thấy sheet Database_Full")
        return
        
    data = db_sheet.get_all_records()
    if not data:
        print("Sheet trống.")
        return
        
    print("2. Đang xử lý dữ liệu (Lọc 30 ngày & Tính trung bình)...")
    transformer = DataTransformer()
    output_data = transformer.calculate_daily_averages(data, days=30)
    
    if len(output_data) <= 1:
        print("Không có task nào trong 30 ngày qua!")
        return
        
    print("3. Đang ghi lên Sheet 'Dashboard_30_Days' và vẽ biểu đồ...")
    try:
        dash_sheet = spreadsheet.worksheet('Dashboard_30_Days')
        spreadsheet.del_worksheet(dash_sheet)
    except gspread.exceptions.WorksheetNotFound:
        pass
        
    dash_sheet = spreadsheet.add_worksheet(title='Dashboard_30_Days', rows="100", cols="10")
    dash_sheet.update(values=output_data, range_name='A1')
    
    # 4. Vẽ biểu đồ bằng Google Sheets API (batch_update)
    sheet_id = dash_sheet.id
    row_count = len(output_data)
    
    chart_request = {
        "requests": [
            {
                "addChart": {
                    "chart": {
                        "spec": {
                            "title": "Phong độ trung bình 30 ngày",
                            "basicChart": {
                                "chartType": "LINE",
                                "legendPosition": "BOTTOM_LEGEND",
                                "axis": [
                                    {"position": "BOTTOM_AXIS", "title": "Ngày"},
                                    {"position": "LEFT_AXIS", "title": "Điểm số"}
                                ],
                                "domains": [{
                                    "domain": {
                                        "sourceRange": {
                                            "sources": [{
                                                "sheetId": sheet_id,
                                                "startRowIndex": 0,
                                                "endRowIndex": row_count,
                                                "startColumnIndex": 0,
                                                "endColumnIndex": 1
                                            }]
                                        }
                                    }
                                }],
                                "series": [{
                                    "series": {
                                        "sourceRange": {
                                            "sources": [{
                                                "sheetId": sheet_id,
                                                "startRowIndex": 0,
                                                "endRowIndex": row_count,
                                                "startColumnIndex": 1,
                                                "endColumnIndex": 2
                                            }]
                                        }
                                    },
                                    "targetAxis": "LEFT_AXIS"
                                }],
                                "headerCount": 1
                            }
                        },
                        "position": {
                            "overlayPosition": {
                                "anchorCell": {
                                    "sheetId": sheet_id,
                                    "rowIndex": 1,
                                    "columnIndex": 3
                                },
                                "widthPixels": 800,
                                "heightPixels": 450
                            }
                        }
                    }
                }
            }
        ]
    }
    
    spreadsheet.batch_update(chart_request)
    print("✅ Đã vẽ xong đồ thị trực tiếp trên Google Sheets!")

if __name__ == "__main__":
    main()
