import uvicorn
from pyngrok import ngrok
import sys
import os

# Đảm bảo import được file webhook_server
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from webhook_server import app

def main():
    try:
        # Khởi tạo Ngrok tunnel ở port 8000
        print("Đang khởi tạo Ngrok Tunnel...")
        public_url = ngrok.connect(8000).public_url
        print("\n" + "="*60)
        print("✅ NGROK ĐÃ CHẠY THÀNH CÔNG!")
        print(f"🔗 Hãy dùng link này để đăng ký: {public_url}/clickup-webhook")
        print("="*60 + "\n")
        
        # Chạy server FastAPI
        uvicorn.run(app, host="0.0.0.0", port=8000)
    except Exception as e:
        print("\n❌ Lỗi khi khởi động Ngrok. Bạn đã thêm Authtoken chưa?")
        print("Hướng dẫn: Chạy lệnh `ngrok config add-authtoken <TOKEN_CỦA_BẠN>` (lấy trên web ngrok.com)")
        print(f"Chi tiết lỗi: {e}")

if __name__ == '__main__':
    main()
