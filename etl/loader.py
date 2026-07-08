import gspread

class SheetsLoader:
    def __init__(self, sheet_client):
        """
        Khởi tạo SheetsLoader với một client của gspread đã được xác thực.
        """
        self.client = sheet_client
        self.main_sheet = None
        self.dashboard_sheet = None

    def set_spreadsheet(self, spreadsheet_name: str):
        """
        Mở file spreadsheet và gán các sheet tương ứng (tạo Dashboard_View nếu chưa có).
        """
        spreadsheet = self.client.open(spreadsheet_name)
        self.main_sheet = spreadsheet.worksheet('Sheet1')
        
        try:
            self.dashboard_sheet = spreadsheet.worksheet('Dashboard_View')
        except gspread.exceptions.WorksheetNotFound:
            self.dashboard_sheet = spreadsheet.add_worksheet(title='Dashboard_View', rows="1000", cols="10")

    def append_new_task(self, row_data: list):
        """
        Thêm một dòng mới vào Sheet gốc (Data Warehouse).
        """
        if self.main_sheet:
            self.main_sheet.append_row(row_data)

    def update_dashboard_view(self, filtered_data: list):
        """
        Xóa dữ liệu cũ trên Dashboard_View và cập nhật khối dữ liệu 30 ngày mới.
        """
        if self.dashboard_sheet and filtered_data:
            self.dashboard_sheet.clear()
            self.dashboard_sheet.update(values=filtered_data, range_name='A1')
