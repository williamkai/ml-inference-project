import requests
from concurrent.futures import ThreadPoolExecutor
import os
import time

# ===========================
# 可調整參數
# ===========================
URL = "http://127.0.0.1:8000/predict"  # FastAPI /predict URL
IMAGE_DIR = "./ts_png"                  # 測試圖片資料夾
MAX_WORKERS = 10                         # 同時併發線程數
ITERATIONS = 2                          # 每張圖片重複測試幾次
# ===========================

# 找出所有 PNG 圖片
images = [os.path.join(IMAGE_DIR, f) for f in os.listdir(IMAGE_DIR) if f.endswith(".png")]

# 將每張圖片重複 ITERATIONS 次
all_images = images * ITERATIONS

def send_request(img_path):
    """對單張圖片發送 POST 請求，並印出回傳結果和耗時"""
    start = time.time()
    try:
        with open(img_path, "rb") as f:
            files = {"file": f}
            response = requests.post(URL, files=files)
        end = time.time()
        if response.status_code == 200:
            pred = response.json().get("prediction")
            print(f"{img_path} -> Prediction: {pred} ({end-start:.3f} 秒)")
        else:
            print(f"{img_path} -> Status code: {response.status_code}, {response.text}")
    except Exception as e:
        end = time.time()
        print(f"{img_path} -> Error: {e} ({end-start:.3f} 秒)")

if __name__ == "__main__":
    print(f"總共有 {len(all_images)} 張圖片要測試，使用 {MAX_WORKERS} 個線程")

    total_start = time.time()
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        executor.map(send_request, all_images)
    total_end = time.time()

    print(f"批量測試完成，總耗時: {total_end - total_start:.2f} 秒")
