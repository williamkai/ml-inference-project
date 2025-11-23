FROM python:3.12-slim

WORKDIR /app

# 安裝系統套件並清理暫存
RUN apt-get update && apt-get install -y --no-install-recommends \
    libjpeg-dev \
    && rm -rf /var/lib/apt/lists/*

# 複製並安裝 Python 套件
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製整個專案
COPY . /app

# 對 Render 免費方案，單 worker
EXPOSE 8000

# 使用單 worker 運行 FastAPI 應用
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]


# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
