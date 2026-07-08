import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()
API_TOKEN = os.environ.get("CLICKUP_API_TOKEN")
headers = {"Authorization": API_TOKEN}

task_id = "86ex48zcb"
url = f"https://api.clickup.com/api/v2/task/{task_id}"
params = {"custom_task_ids": "true", "team_id": "90182539297"}
response = requests.get(url, headers=headers, params=params)

if response.status_code == 200:
    task = response.json()
    dates = {k: v for k, v in task.items() if 'date' in k}
    print(json.dumps(dates, indent=2))
