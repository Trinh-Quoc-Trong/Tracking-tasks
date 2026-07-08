from datetime import datetime, timedelta
from collections import defaultdict

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
    def extract_field(custom_fields: list, target_keywords: list) -> str:
        """Tìm và trích xuất giá trị từ Custom Fields dựa trên từ khóa."""
        for field in custom_fields:
            name = field.get('name', '').lower()
            if any(kw in name for kw in target_keywords):
                return field.get('value', "")
        return ""

    def format_task_to_row(self, task: dict) -> list:
        """
        Biến đổi một object JSON Task nguyên bản thành một List 1D để ghi vào Google Sheets.
        Format: [Task ID, Tên Task, Trạng thái, Ngày hoàn thành, Năng lực, Mục tiêu]
        """
        task_id = task.get("id", "")
        name = task.get("name", "")
        
        status_info = task.get("status", {})
        status_name = status_info.get("status", "")
        status_type = status_info.get("type", "")
        
        end_time = self.format_timestamp(task.get("date_closed"))
        
        custom_fields = task.get("custom_fields", [])
        score_nang_luc = self.extract_field(custom_fields, ["năng lực"])
        score_muc_tieu = self.extract_field(custom_fields, ["mục tiêu"])
        
        return [task_id, name, status_name, end_time, score_nang_luc, score_muc_tieu]

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
        Tính điểm số trung bình (Năng lực + Mục tiêu) của từng ngày dựa trên danh sách data.
        Đầu ra là danh sách mảng 2 chiều [Ngày, Điểm trung bình].
        """
        daily_scores = defaultdict(list)
        
        for row in data_rows:
            if not row or len(row) < 6:
                continue
                
            date_str = row[3]
            try:
                # Chuyển từ "YYYY-MM-DD HH:MM:SS" sang "YYYY-MM-DD"
                task_date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                day_key = task_date.strftime("%Y-%m-%d")
            except ValueError:
                continue
                
            try:
                nang_luc = float(row[4] or 0)
            except ValueError:
                nang_luc = 0.0
                
            try:
                muc_tieu = float(row[5] or 0)
            except ValueError:
                muc_tieu = 0.0
                
            total_score = nang_luc + muc_tieu
            daily_scores[day_key].append(total_score)
            
        # Tính trung bình và sort theo ngày
        output = [["Ngày", "Điểm số"]]
        sorted_days = sorted(daily_scores.keys())
        
        for day in sorted_days:
            scores = daily_scores[day]
            if scores:
                avg_score = sum(scores) / len(scores)
                output.append([day, round(avg_score, 2)])
                
        return output
