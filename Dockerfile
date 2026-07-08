FROM python:3.10-slim

WORKDIR /app

# Khắc phục lỗi timezone nếu có
ENV TZ=Asia/Ho_Chi_Minh
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ mã nguồn vào Container
COPY . .

# Chạy server
CMD ["python", "scripts/start_server.py"]
