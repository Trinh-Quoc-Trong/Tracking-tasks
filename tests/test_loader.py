import pytest
from unittest.mock import MagicMock
from etl.loader import SheetsLoader

class TestSheetsLoader:
    
    def test_initialization(self):
        mock_client = MagicMock()
        mock_spreadsheet = MagicMock()
        mock_client.open_by_url.return_value = mock_spreadsheet
        
        # Giả lập sheet tồn tại
        mock_spreadsheet.worksheet.return_value = MagicMock()
        
        loader = SheetsLoader(mock_client, "http://fake.url")
        
        mock_client.open_by_url.assert_called_with("http://fake.url")
        assert loader.db_sheet is not None
        assert loader.dashboard_sheet is not None

    def test_append_new_task(self):
        mock_client = MagicMock()
        loader = SheetsLoader(mock_client, "url")
        
        mock_db_sheet = MagicMock()
        loader.db_sheet = mock_db_sheet
        
        row_data = ["123", "Task", "Closed"]
        loader.append_new_task(row_data)
        
        mock_db_sheet.append_row.assert_called_once_with(row_data)

    def test_bulk_update_database(self):
        mock_client = MagicMock()
        loader = SheetsLoader(mock_client, "url")
        
        mock_db_sheet = MagicMock()
        loader.db_sheet = mock_db_sheet
        
        table_data = [["A", "B"], ["1", "2"]]
        loader.bulk_update_database(table_data)
        
        mock_db_sheet.clear.assert_called_once()
        mock_db_sheet.update.assert_called_once_with(values=table_data, range_name='A1')

    def test_update_dashboard_view(self):
        mock_client = MagicMock()
        loader = SheetsLoader(mock_client, "url")
        
        mock_dash_sheet = MagicMock()
        loader.dashboard_sheet = mock_dash_sheet
        
        filtered_data = [["Ngày", "Điểm"], ["2023-01-01", 10.0]]
        loader.update_dashboard_view(filtered_data)
        
        mock_dash_sheet.clear.assert_called_once()
        mock_dash_sheet.update.assert_called_once_with(values=filtered_data, range_name='A1')
