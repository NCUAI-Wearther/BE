# 使用官方 Python 基礎映像
FROM python:3.10-slim

# 設定工作目錄
WORKDIR /app

# 複製必要的檔案
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# 啟動 Flask 伺服器（可改為你實際的啟動命令）
CMD ["python", "main.py"]
