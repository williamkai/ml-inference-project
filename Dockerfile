# 使用官方 Python 映像，這裡用 3.12 slim 版本
FROM python:3.12-slim

# 設定工作目錄
WORKDIR /app

# 複製 requirements.txt 並安裝套件
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 複製專案程式碼到容器內
COPY . /app

# 對外開放 8000 port
EXPOSE 8000

# 設定容器啟動指令，支援多線程併發
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
