import requests

class ClickUpExtractor:
    def __init__(self, api_token: str, list_id: str):
        self.api_token = api_token
        self.list_id = list_id
        
    def fetch_closed_tasks(self) -> list:
        """
        Gửi request đến API của ClickUp để lấy các task có trạng thái 'closed'.
        """
        url = f"https://api.clickup.com/api/v2/list/{self.list_id}/task"
        headers = {
            "Authorization": self.api_token
        }
        params = {
            "statuses[]": "closed",
            "subtasks": "true"
        }
        
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            return data.get('tasks', [])
        else:
            raise Exception(f"Loi goi API: {response.status_code} - {response.text}")
