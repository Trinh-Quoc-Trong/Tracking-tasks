import os
import requests
from dotenv import load_dotenv

load_dotenv()
API_TOKEN = os.environ.get("CLICKUP_API_TOKEN")
TEAM_ID = os.environ.get("CLICKUP_TEAM_ID")

def register_webhook(webhook_url: str):
    url = f"https://api.clickup.com/api/v2/team/{TEAM_ID}/webhook"
    headers = {
        "Authorization": API_TOKEN,
        "Content-Type": "application/json"
    }
    # Chỉ bắt sự kiện cập nhật trạng thái Task để tiết kiệm tài nguyên
    payload = {
        "endpoint": webhook_url,
        "events": [
            "taskStatusUpdated"
        ]
    }
    
    print(f"Đang gửi yêu cầu đăng ký Webhook tới ClickUp...")
    print(f"URL Đích: {webhook_url}")
    print("Xin chờ...")
    
    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code == 200:
        print("✅ ĐĂNG KÝ WEBHOOK THÀNH CÔNG!")
        data = response.json()
        print(f"Webhook ID: {data.get('webhook', {}).get('id')}")
    else:
        print(f"❌ LỖI TỪ CLICKUP: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("⚠️ CÁCH DÙNG: python scripts/register_webhook.py <ĐƯỜNG_LINK_NGROK_WEBHOOK>")
        print("Ví dụ: python scripts/register_webhook.py https://1234-abcd.ngrok.io/clickup-webhook")
        sys.exit(1)
    
    register_webhook(sys.argv[1])
