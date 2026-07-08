import gspread

class SheetsLoader:
    def __init__(self, sheet_client, spreadsheet_url: str):
        """
        Khởi tạo SheetsLoader với một client của gspread và mở Google Sheets thông qua URL.
        """
        self.client = sheet_client
        self.spreadsheet = self.client.open_by_url(spreadsheet_url)
        self.sheet_id = self.spreadsheet.id
        
        # Tạo/Lấy Sheet 'Database_Full'
        try:
            self.db_sheet = self.spreadsheet.worksheet('Database_Full')
        except gspread.exceptions.WorksheetNotFound:
            self.db_sheet = self.spreadsheet.add_worksheet(title='Database_Full', rows="5000", cols="10")
            
        # Tạo/Lấy Sheet 'Dashboard_30_Days'
        try:
            self.dashboard_sheet = self.spreadsheet.worksheet('Dashboard_30_Days')
        except gspread.exceptions.WorksheetNotFound:
            self.dashboard_sheet = self.spreadsheet.add_worksheet(title='Dashboard_30_Days', rows="1000", cols="10")

    def append_new_task(self, row_data: list):
        """Thêm một dòng mới vào Database_Full (Dùng cho Webhook)."""
        if self.db_sheet:
            self.db_sheet.append_row(row_data)

    def bulk_update_database(self, table_data: list):
        """Xóa trắng và ghi đè toàn bộ dữ liệu vào Database_Full (Dùng cho quá trình Init ban đầu)."""
        if self.db_sheet:
            self.db_sheet.clear()
            self.db_sheet.update(values=table_data, range_name='A1')
            
    def get_all_database_records(self) -> list:
        """Lấy toàn bộ dữ liệu hiện tại từ Database_Full để xử lý."""
        if self.db_sheet:
            return self.db_sheet.get_all_values()
        return []

    def update_dashboard_view(self, filtered_data: list):
        """Xóa dữ liệu cũ trên Dashboard_30_Days và cập nhật dữ liệu mới."""
        if self.dashboard_sheet and filtered_data:
            self.dashboard_sheet.clear()
            self.dashboard_sheet.update(values=filtered_data, range_name='A25')

    def draw_chart(self):
        """
        Tự động vẽ đồ thị dạng Line Chart trên sheet 'Dashboard_30_Days'.
        Sử dụng batch_update của API Google Sheets để truyền vào cấu trúc JSON đồ thị.
        """
        # Xóa các đồ thị cũ đang có trên sheet này
        existing_charts = self.dashboard_sheet.client.request('get', f'https://sheets.googleapis.com/v4/spreadsheets/{self.sheet_id}').json()
        sheet_metadata = [s for s in existing_charts.get('sheets', []) if s.get('properties', {}).get('title') == 'Dashboard_30_Days']
        
        if sheet_metadata:
            charts = sheet_metadata[0].get('charts', [])
            if charts:
                delete_requests = [{"deleteEmbeddedObject": {"objectId": chart.get('chartId')}} for chart in charts]
                self.spreadsheet.batch_update({"requests": delete_requests})

        # Tạo Yêu cầu vẽ đồ thị Line Chart mới
        sheet_id_num = self.dashboard_sheet.id
        request = {
            "requests": [
                {
                    "addChart": {
                        "chart": {
                            "spec": {
                                "title": "Phong độ trung bình 30 ngày (Năng lực + Mục tiêu)",
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
                                                    "sheetId": sheet_id_num,
                                                    "startRowIndex": 24,
                                                    "endRowIndex": 55,
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
                                                    "sheetId": sheet_id_num,
                                                    "startRowIndex": 24,
                                                    "endRowIndex": 55,
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
                                        "sheetId": sheet_id_num,
                                        "rowIndex": 0,
                                        "columnIndex": 0
                                    },
                                    "offsetXPixels": 10,
                                    "offsetYPixels": 10,
                                    "widthPixels": 800,
                                    "heightPixels": 450
                                }
                            }
                        }
                    }
                }
            ]
        }
        self.spreadsheet.batch_update(request)
