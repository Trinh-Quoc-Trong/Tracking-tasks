import requests
import subprocess
import time

try:
    # Hỏi thăm Ngrok xem nó đang tạo ra đường link public nào
    response = requests.get("http://127.0.0.1:4040/api/tunnels")
    tunnels = response.json().get("tunnels", [])
    
    public_url = None
    for t in tunnels:
        if t["proto"] == "https":
            public_url = t["public_url"]
            break
            
    if public_url:
        webhook_url = f"{public_url}/clickup-webhook"
        print(f"✨ TỰ ĐỘNG TÌM THẤY NGROK URL: {webhook_url}")
        print("🤖 Đang chạy tự động Bước 3 cho bạn...")
        
        # Gọi thẳng script register
        subprocess.run(["conda", "run", "-n", "etl-tracker", "python", "scripts/register_webhook.py", webhook_url])
    else:
        print("❌ Không tìm thấy link ngrok. Có vẻ Server chưa chạy lên hoàn toàn.")
except Exception as e:
    print(f"❌ Lỗi khi tự động tìm link: {e}")
