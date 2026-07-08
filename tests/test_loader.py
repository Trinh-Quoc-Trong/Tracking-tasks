import pytest
from unittest.mock import MagicMock

# Import class SheetsLoader (File etl/loader.py hiện đang trống)
from etl.loader import SheetsLoader

class TestSheetsLoader:
    
    def test_append_new_task(self):
        """Test việc gọi API thêm 1 dòng mới vào Google Sheets."""
        # Mock đối tượng Google Sheet (worksheet)
        mock_sheet = MagicMock()
        
        loader = SheetsLoader(sheet_client=MagicMock())
        # Cố tình ghi đè sheet thành đối tượng mock để kiểm tra
        loader.main_sheet = mock_sheet
        
        row_data = ["2026-07-07 10:00:00", "id1", "Task Name", "9.0"]
        loader.append_new_task(row_data)
        
        # Kiểm tra xem hàm append_row có được gọi với đúng data không
        mock_sheet.append_row.assert_called_once_with(row_data)

    def test_update_dashboard_view(self):
        """Test logic cập nhật Dashboard View (Xóa dữ liệu cũ và cập nhật dữ liệu mới)."""
        mock_dashboard_sheet = MagicMock()
        
        loader = SheetsLoader(sheet_client=MagicMock())
        loader.dashboard_sheet = mock_dashboard_sheet
        
        filtered_data = [
            ["Date", "Task ID", "Name", "Score"],
            ["2026-07-07 10:00:00", "id1", "Task Name", "9.0"]
        ]
        
        loader.update_dashboard_view(filtered_data)
        
        # Kiểm tra Dashboard đã được clear chưa
        mock_dashboard_sheet.clear.assert_called_once()
        # Kiểm tra Dashboard đã được update dòng mới chưa
        mock_dashboard_sheet.update.assert_called_once_with(values=filtered_data, range_name='A1')
