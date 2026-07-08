import requests

class ClickUpExtractor:
    def __init__(self, api_token: str, team_id: str):
        self.api_token = api_token
        self.team_id = team_id
        
    def fetch_all_workspace_tasks(self, include_closed: bool = True) -> list:
        """
        Quét toàn bộ task trong Workspace có hỗ trợ phân trang (Pagination).
        """
        url = f"https://api.clickup.com/api/v2/team/{self.team_id}/task"
        headers = {"Authorization": self.api_token}
        
        all_tasks = []
        page = 0
        while True:
            params = {
                "subtasks": "true",
                "include_closed": str(include_closed).lower(),
                "page": page
            }
            resp = requests.get(url, headers=headers, params=params)
            if resp.status_code != 200:
                raise Exception(f"Lỗi gọi API: {resp.status_code} - {resp.text}")
                
            tasks = resp.json().get('tasks', [])
            if not tasks:
                break
                
            all_tasks.extend(tasks)
            page += 1
            
            # ClickUp trả về tối đa 100 task mỗi trang. Nếu ít hơn 100 nghĩa là trang cuối.
            if len(tasks) < 100:
                break
                
        return all_tasks

    def fetch_task_details(self, task_id: str) -> dict:
        """
        Gọi API lấy chi tiết 1 task (Sử dụng cho Webhook khi cần lấy Custom Fields).
        """
        url = f"https://api.clickup.com/api/v2/task/{task_id}"
        headers = {"Authorization": self.api_token}
        params = {
            "custom_task_ids": "true",
            "team_id": self.team_id
        }
        resp = requests.get(url, headers=headers, params=params)
        
        if resp.status_code == 200:
            return resp.json()
        raise Exception(f"Không thể lấy thông tin task {task_id}: {resp.status_code}")
