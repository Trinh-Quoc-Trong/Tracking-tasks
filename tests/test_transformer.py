import pytest
from datetime import datetime, timedelta

from etl.transformer import DataTransformer

class TestDataTransformer:
    
    def test_extract_performance_score(self):
        """Test việc bóc tách đúng điểm Performance Score từ mảng custom_fields của ClickUp."""
        raw_task = {
            "id": "123",
            "name": "Nghiên cứu AI",
            "custom_fields": [
                {"name": "Trạng thái", "value": "Done"},
                {"name": "🔌 Hiệu xuất với mục tiêu", "value": 9.5}
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
        
        mock_sheet_data = [
            ["Date", "Task ID", "Name", "Score"],
            [yesterday.strftime(date_format), "1", "Task Hôm Qua", "9"],
            [forty_days_ago.strftime(date_format), "2", "Task Quá Hạn", "8"]
        ]
        
        transformer = DataTransformer()
        filtered_data = transformer.filter_last_30_days(mock_sheet_data)
        
        assert len(filtered_data) == 2
        assert filtered_data[1][2] == "Task Hôm Qua"

    def test_calculate_daily_averages(self):
        """Test TDD: Kiểm tra logic tính điểm trung bình (Năng lực + Mục tiêu) nhóm theo ngày."""
        today = datetime.now()
        yesterday = today - timedelta(days=1)
        two_days_ago = today - timedelta(days=2)
        forty_days_ago = today - timedelta(days=40)
        
        date_format = "%Y-%m-%d %H:%M:%S"
        
        mock_data = [
            {
                "Ngày hoàn thành (End Time)": yesterday.strftime(date_format),
                "Hiệu suất với năng lực": 4,
                "Hiệu xuất với mục tiêu": 5
            },
            {
                "Ngày hoàn thành (End Time)": yesterday.strftime(date_format),
                "Hiệu suất với năng lực": 3,
                "Hiệu xuất với mục tiêu": 4
            },
            {
                "Ngày hoàn thành (End Time)": two_days_ago.strftime(date_format),
                "Hiệu suất với năng lực": "5",
                "Hiệu xuất với mục tiêu": ""
            },
            {
                "Ngày hoàn thành (End Time)": forty_days_ago.strftime(date_format),
                "Hiệu suất với năng lực": 10,
                "Hiệu xuất với mục tiêu": 10
            }
        ]
        
        transformer = DataTransformer()
        result = transformer.calculate_daily_averages(mock_data, days=30)
        
        # Mong đợi: 1 header + 2 ngày hợp lệ (two_days_ago, yesterday)
        assert len(result) == 3
        
        assert result[0] == ["Ngày", "Điểm trung bình (Năng lực + Mục tiêu)"]
        
        # Test 1: two_days_ago -> 1 task: Năng lực=5, Mục tiêu=0 -> Tổng=5 -> TB=5.0
        assert result[1][0] == two_days_ago.strftime("%Y-%m-%d")
        assert result[1][1] == 5.0
        
        # Test 2: yesterday -> 2 task: (4+5=9) và (3+4=7) -> Tổng 2 task = 16 -> TB = 8.0
        assert result[2][0] == yesterday.strftime("%Y-%m-%d")
        assert result[2][1] == 8.0
