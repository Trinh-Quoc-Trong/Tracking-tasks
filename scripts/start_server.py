import uvicorn
from pyngrok import ngrok
import sys
import os
import requests
import time

# Đảm bảo import được file webhook_server
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from webhook_server import app
from core.config import settings

def clear_and_register_webhook(public_url: str):
    """
    Xóa tất cả các webhook cũ có chứa domain ngrok và đăng ký webhook mới.
    """
    base_url = f"https://api.clickup.com/api/v2/team/{settings.CLICKUP_TEAM_ID}/webhook"
    headers = {
        "Authorization": settings.CLICKUP_API_TOKEN,
        "Content-Type": "application/json"
    }
    
    # 1. Quét và xóa Webhook cũ
    print("-> Đang kiểm tra và dọn dẹp các Webhook ngrok cũ trên ClickUp...")
    resp = requests.get(base_url, headers=headers)
    if resp.status_code == 200:
        webhooks = resp.json().get('webhooks', [])
        for wh in webhooks:
            endpoint = wh.get('endpoint', '')
            if 'ngrok' in endpoint:
                wh_id = wh.get('id')
                print(f"   [Xóa] Phát hiện webhook cũ: {endpoint} (ID: {wh_id})")
                requests.delete(f"https://api.clickup.com/api/v2/webhook/{wh_id}", headers=headers)
    else:
        print("   [Cảnh báo] Không lấy được danh sách webhook cũ.")

    # 2. Đăng ký Webhook mới
    payload = {
        "endpoint": f"{public_url}/clickup-webhook",
        "events": ["taskStatusUpdated"]
    }
    print(f"-> Đang đăng ký Webhook mới: {payload['endpoint']}")
    reg_resp = requests.post(base_url, headers=headers, json=payload)
    
    if reg_resp.status_code == 200:
        data = reg_resp.json()
        print(f"✅ ĐĂNG KÝ WEBHOOK TỰ ĐỘNG THÀNH CÔNG! (ID: {data.get('webhook', {}).get('id')})")
    else:
        print(f"❌ Lỗi đăng ký Webhook: {reg_resp.status_code} - {reg_resp.text}")

def main():
    try:
        # Cấu hình authtoken cho ngrok từ biến môi trường
        ngrok.set_auth_token(settings.NGROK_AUTHTOKEN)
        
        # Khởi tạo Ngrok tunnel ở port 8000
        print("Đang khởi tạo Ngrok Tunnel...")
        public_url = ngrok.connect(8000).public_url
        print("\n" + "="*60)
        print("✅ NGROK ĐÃ CHẠY THÀNH CÔNG!")
        print(f"🔗 URL Cổng kết nối: {public_url}")
        print("="*60 + "\n")
        
        # Tự động hóa đăng ký Webhook với ClickUp
        clear_and_register_webhook(public_url)
        
        # Chạy server FastAPI
        print("\n🚀 Đang khởi động Webhook Server...")
        uvicorn.run(app, host="0.0.0.0", port=8000)
    except Exception as e:
        print("\n❌ Lỗi khi khởi động Hệ thống!")
        print(f"Chi tiết lỗi: {e}")

if __name__ == '__main__':
    main()
