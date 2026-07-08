from datetime import datetime, timedelta
from collections import defaultdict

class DataTransformer:
    def extract_score(self, raw_task: dict):
        """Bóc tách điểm Hiệu suất từ mảng custom_fields của ClickUp."""
        for field in raw_task.get('custom_fields', []):
            name = field.get('name', '').lower()
            if 'hiệu xuất với mục tiêu' in name or 'hiệu suất với mục tiêu' in name:
                return field.get('value')
        return None

    def filter_last_30_days(self, sheet_data: list) -> list:
        """Lọc dữ liệu Google Sheets để chỉ lấy 30 ngày gần nhất (kèm header)."""
        if not sheet_data or len(sheet_data) <= 1:
            return sheet_data
            
        headers = sheet_data[0]
        data_rows = sheet_data[1:]
        
        thirty_days_ago = datetime.now() - timedelta(days=30)
        filtered_data = [headers]
        
        for row in data_rows:
            try:
                row_date = datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S")
                if row_date >= thirty_days_ago:
                    filtered_data.append(row)
            except (ValueError, IndexError):
                continue
                
        return filtered_data

    def calculate_daily_averages(self, data_rows: list[dict], days: int = 30) -> list[list]:
        """Tối ưu TDD: Tính điểm trung bình mỗi ngày trong vòng `days` ngày qua. Trả về mảng 2D cho Sheet."""
        limit_date = datetime.now() - timedelta(days=days)
        daily_stats = defaultdict(lambda: {"sum": 0.0, "count": 0})
        
        for row in data_rows:
            end_time_str = row.get('Ngày hoàn thành (End Time)', '')
            if not end_time_str:
                continue
                
            try:
                end_time = datetime.strptime(end_time_str, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                continue
                
            if end_time < limit_date:
                continue
                
            date_str = end_time.strftime("%Y-%m-%d")
            
            try:
                nang_luc = float(row.get('Hiệu suất với năng lực') or 0)
            except ValueError:
                nang_luc = 0.0
                
            try:
                muc_tieu = float(row.get('Hiệu xuất với mục tiêu') or 0)
            except ValueError:
                muc_tieu = 0.0
                
            total_score = nang_luc + muc_tieu
            
            daily_stats[date_str]["sum"] += total_score
            daily_stats[date_str]["count"] += 1
            
        output_data = [["Ngày", "Điểm trung bình (Năng lực + Mục tiêu)"]]
        
        for d in sorted(daily_stats.keys()):
            stats = daily_stats[d]
            avg = round(stats["sum"] / stats["count"], 2)
            output_data.append([d, avg])
            
        return output_data
