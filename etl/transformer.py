from datetime import datetime, timedelta
from collections import defaultdict

import re

class DataTransformer:
    
    @staticmethod
    def format_timestamp(ts_str: str) -> str:
        """Đổi timestamp millisecond của ClickUp sang dạng chuỗi YYYY-MM-DD HH:MM:SS."""
        if not ts_str:
            return ""
        try:
            ts = int(ts_str) / 1000.0
            return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            return ""

    @staticmethod
    def extract_score_from_description(description: str) -> str:
        """Trích xuất con số đầu tiên (từ 1 đến 10) trong phần description."""
        if not description:
            return ""
        # Match các số từ 1 đến 10, đứng độc lập (không nằm trong 1 từ khác)
        match = re.search(r'\b([1-9]|10)\b', str(description))
        if match:
            return match.group(1)
        return ""

    def format_task_to_row(self, task: dict) -> list:
        """
        Biến đổi một object JSON Task nguyên bản thành một List 1D để ghi vào Google Sheets.
        Format: [Task ID, Tên Task, Trạng thái, Ngày hoàn thành, Điểm số]
        """
        task_id = task.get("id", "")
        name = task.get("name", "")
        
        status_info = task.get("status", {})
        status_name = status_info.get("status", "")
        status_type = status_info.get("type", "")
        
        end_time = self.format_timestamp(task.get("date_closed"))
        
        description = task.get("description", "") or task.get("text_content", "")
        score = self.extract_score_from_description(description)
        
        return [task_id, name, status_name, end_time, score]

    def filter_last_30_days(self, data_rows: list) -> list:
        """
        Lọc các row dữ liệu, chỉ lấy những task được đóng trong vòng 30 ngày qua.
        """
        filtered_data = []
        thirty_days_ago = datetime.now() - timedelta(days=30)
        
        for row in data_rows:
            if not row or len(row) < 4:
                continue
            date_str = row[3] # Index 3 là Ngày hoàn thành (End Time)
            if not date_str or date_str == "Ngày hoàn thành (End Time)":
                continue
                
            try:
                task_date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                if task_date >= thirty_days_ago:
                    filtered_data.append(row)
            except ValueError:
                pass # Bỏ qua các dòng bị lỗi format ngày tháng
                
        return filtered_data
        
    def calculate_daily_averages(self, data_rows: list) -> list:
        """
        Tính điểm số trung bình của từng ngày. Lấp đầy đủ 30 ngày gần nhất (những ngày không có task sẽ là 0).
        """
        daily_scores = defaultdict(list)
        
        for row in data_rows:
            if not row or len(row) < 5:
                continue
                
            date_str = row[3]
            try:
                # Chuyển từ "YYYY-MM-DD HH:MM:SS" sang "YYYY-MM-DD"
                task_date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                day_key = task_date.strftime("%Y-%m-%d")
            except ValueError:
                continue
                
            try:
                total_score = float(row[4] or 0)
            except ValueError:
                total_score = 0.0
                
            daily_scores[day_key].append(total_score)
            
        output = [["Ngày", "Điểm số"]]
        
        # Lấp đầy đủ 30 ngày (từ 29 ngày trước đến hôm nay)
        today = datetime.now()
        for i in range(29, -1, -1):
            day_dt = today - timedelta(days=i)
            day = day_dt.strftime("%Y-%m-%d")
            
            scores = daily_scores.get(day)
            if scores:
                avg_score = sum(scores) / len(scores)
                output.append([day, round(avg_score, 2)])
            else:
                output.append([day, 0.0])
                
        return output
