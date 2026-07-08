import os
import requests
from dotenv import load_dotenv

load_dotenv()
API_TOKEN = os.environ.get("CLICKUP_API_TOKEN")
TEAM_ID = os.environ.get("CLICKUP_TEAM_ID")
headers = {"Authorization": API_TOKEN}

url = f"https://api.clickup.com/api/v2/team/{TEAM_ID}/task"
params = {"page": 0, "include_closed": "true"}

print("Đang gọi thử API của ClickUp...")
response = requests.get(url, headers=headers, params=params)

if response.status_code == 200:
    tasks = response.json().get('tasks', [])
    print(f"✅ API hoạt động BÌNH THƯỜNG! Trả về được {len(tasks)} tasks ở trang 0.")
else:
    print(f"❌ Lỗi gọi API: {response.status_code}")
    print(response.text)
