import pytest
from datetime import datetime, timedelta

from etl.transformer import DataTransformer

class TestDataTransformer:
    
    def test_format_timestamp(self):
        transformer = DataTransformer()
        # 1783530697788 ms -> 2026-07-08 23:11:37 (timezone dependent, test a fixed value)
        ts_str = "1700000000000" # 2023-11-14 22:13:20 in UTC+0, this test is local-TZ dependent
        # To avoid TZ issues in test, we just check if it returns a string in correct format
        result = transformer.format_timestamp(ts_str)
        assert len(result) == 19
        assert result.count("-") == 2
        assert result.count(":") == 2
        
        # Test rỗng
        assert transformer.format_timestamp("") == ""
        assert transformer.format_timestamp(None) == ""

    def test_extract_field(self):
        transformer = DataTransformer()
        custom_fields = [
            {"name": "Năng lực chuyên môn", "value": "5"},
            {"name": "Hiệu suất với mục tiêu", "value": "4"}
        ]
        
        assert transformer.extract_field(custom_fields, ["năng lực"]) == "5"
        assert transformer.extract_field(custom_fields, ["mục tiêu"]) == "4"
        assert transformer.extract_field(custom_fields, ["không tồn tại"]) == ""

    def test_format_task_to_row(self):
        transformer = DataTransformer()
        raw_task = {
            "id": "123",
            "name": "Task Test",
            "status": {"status": "Closed", "type": "closed"},
            "date_closed": "1700000000000",
            "custom_fields": [
                {"name": "Năng lực chuyên môn", "value": "3"},
                {"name": "Hiệu suất với mục tiêu", "value": "5"}
            ]
        }
        
        row = transformer.format_task_to_row(raw_task)
        assert len(row) == 6
        assert row[0] == "123"
        assert row[1] == "Task Test"
        assert row[2] == "Closed"
        assert row[4] == "3"
        assert row[5] == "5"

    def test_filter_last_30_days(self):
        transformer = DataTransformer()
        
        # Giả lập ngày hôm nay, 10 ngày trước, 40 ngày trước
        today = datetime.now()
        day_10 = today - timedelta(days=10)
        day_40 = today - timedelta(days=40)
        
        data = [
            ["ID_Hdr", "Tên_Hdr", "Status_Hdr", "Ngày hoàn thành (End Time)", "NL", "MT"],
            ["1", "Task 1", "Closed", today.strftime("%Y-%m-%d %H:%M:%S"), "5", "5"],
            ["2", "Task 2", "Closed", day_10.strftime("%Y-%m-%d %H:%M:%S"), "4", "4"],
            ["3", "Task 3", "Closed", day_40.strftime("%Y-%m-%d %H:%M:%S"), "3", "3"], # Sẽ bị loại
            ["4", "Lỗi format", "Closed", "2024-invalid-date", "0", "0"] # Bị loại
        ]
        
        filtered = transformer.filter_last_30_days(data)
        
        assert len(filtered) == 2
        assert filtered[0][0] == "1"
        assert filtered[1][0] == "2"

    def test_calculate_daily_averages(self):
        transformer = DataTransformer()
        
        today = datetime.now()
        today_str = today.strftime("%Y-%m-%d %H:%M:%S")
        today_key = today.strftime("%Y-%m-%d")
        
        day2 = today - timedelta(days=1)
        day2_str = day2.strftime("%Y-%m-%d %H:%M:%S")
        day2_key = day2.strftime("%Y-%m-%d")
        
        # Tạo dữ liệu test
        # Hôm nay: 2 Task (Task 1: 5+5=10đ, Task 2: 3+5=8đ) -> TB hôm nay = 9.0
        # Hôm qua: 1 Task (Task 3: 4+4=8đ) -> TB hôm qua = 8.0
        data = [
            ["1", "T1", "Closed", today_str, "5", "5"],
            ["2", "T2", "Closed", today_str, "3", "5"],
            ["3", "T3", "Closed", day2_str, "4", "4"],
            ["4", "Lỗi rỗng", "Closed", today_str, "", ""], # (0+0 = 0)
        ]
        
        result = transformer.calculate_daily_averages(data)
        
        assert len(result) == 3 # Header + 2 ngày
        assert result[0] == ["Ngày", "Điểm số"]
        
        # Kết quả đã được sort theo ngày (ngày hôm qua đứng trước)
        assert result[1][0] == day2_key
        assert result[1][1] == 8.0
        
        # TB hôm nay là (10 + 8 + 0) / 3 = 6.0
        assert result[2][0] == today_key
        assert result[2][1] == 6.0
