import pytest
from datetime import datetime, timedelta

# Import class DataTransformer (File etl/transformer.py hiện đang trống)
from etl.transformer import DataTransformer

class TestDataTransformer:
    
    def test_extract_performance_score(self):
        """Test việc bóc tách đúng điểm Performance Score từ mảng custom_fields của ClickUp."""
        raw_task = {
            "id": "123",
            "name": "Nghiên cứu AI",
            "custom_fields": [
                {"name": "Trạng thái", "value": "Done"},
                {"name": "Performance Score", "value": 9.5}
            ]
        }
        
        transformer = DataTransformer()
        score = transformer.extract_score(raw_task)
        
        assert score == 9.5

    def test_extract_score_missing_field(self):
        """Test trường hợp task không có trường Performance Score."""
        raw_task = {
            "id": "124",
            "name": "Họp team",
            "custom_fields": [
                {"name": "Trạng thái", "value": "Done"}
            ]
        }
        
        transformer = DataTransformer()
        score = transformer.extract_score(raw_task)
        
        assert score is None

    def test_filter_30_days_data(self):
        """Test logic lọc dữ liệu chỉ lấy 30 ngày gần nhất."""
        today = datetime.now()
        yesterday = today - timedelta(days=1)
        forty_days_ago = today - timedelta(days=40)
        
        date_format = "%Y-%m-%d %H:%M:%S"
        
        # Headers + 2 dòng dữ liệu (1 hợp lệ, 1 quá hạn)
        mock_sheet_data = [
            ["Date", "Task ID", "Name", "Score"],
            [yesterday.strftime(date_format), "1", "Task Hôm Qua", "9"],
            [forty_days_ago.strftime(date_format), "2", "Task Quá Hạn", "8"]
        ]
        
        transformer = DataTransformer()
        filtered_data = transformer.filter_last_30_days(mock_sheet_data)
        
        # Header + 1 dòng hợp lệ = 2 dòng
        assert len(filtered_data) == 2
        assert filtered_data[1][2] == "Task Hôm Qua"
