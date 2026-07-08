import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()
API_TOKEN = os.environ.get("CLICKUP_API_TOKEN")
headers = {"Authorization": API_TOKEN}

task_id = "86ex48zcb"
print(f"Đang gọi API trực tiếp để lấy thông tin Task ID: {task_id}...")

url = f"https://api.clickup.com/api/v2/task/{task_id}"
params = {
    "custom_task_ids": "true",
    "team_id": "90182539297" 
}

response = requests.get(url, headers=headers, params=params)

if response.status_code == 200:
    target_task = response.json()
    print(f"\n✅ Đã tìm thấy task: '{target_task.get('name')}'!")
    
    summary = {
        "id": target_task.get("id"),
        "name": target_task.get("name"),
        "status": target_task.get("status"),
        "list": {"id": target_task.get("list", {}).get("id")},
        "custom_fields": target_task.get("custom_fields", [])
    }
    
    print("\n--- JSON DATA THU GỌN ---")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    
    print("\n--- TẤT CẢ CÁC TRƯỜNG CUSTOM FIELDS ---")
    for field in target_task.get('custom_fields', []):
        print(f"🎯 Tên Field: '{field.get('name')}'")
        print(f"   Value: {field.get('value')}")
        print(f"   Type: {field.get('type')}")
        print("   ---")
else:
    print(f"❌ Không tìm thấy task. Lỗi trả về: {response.status_code} - {response.text}")
