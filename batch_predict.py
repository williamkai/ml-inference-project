import os
import csv
import asyncio
import httpx

# ====== 設定 ======
API_URL = "http://localhost:8000/predict"  # 替換成你的 FastAPI URL
IMAGE_DIR = "test"
OUTPUT_CSV = "result.csv"
CONCURRENT_REQUESTS = 10  # 同時發送幾個請求，可調整

async def predict_image(client, img_name):
    img_path = os.path.join(IMAGE_DIR, img_name)
    if not os.path.isfile(img_path):
        return img_name, None
    try:
        with open(img_path, "rb") as f:
            files = {"file": (img_name, f, "image/jpeg")}
            response = await client.post(API_URL, files=files)
            response.raise_for_status()
            pred = response.json().get("prediction")  # 根據你的 API 回傳調整 key
        return img_name, pred
    except Exception as e:
        print(f"Error processing {img_name}: {e}")
        return img_name, None

async def batch_predict():
    image_list = [f for f in os.listdir(IMAGE_DIR) if os.path.isfile(os.path.join(IMAGE_DIR, f))]
    results = []

    async with httpx.AsyncClient(timeout=60) as client:
        semaphore = asyncio.Semaphore(CONCURRENT_REQUESTS)

        async def sem_task(img):
            async with semaphore:
                return await predict_image(client, img)

        tasks = [sem_task(img) for img in image_list]
        for future in asyncio.as_completed(tasks):
            img_name, pred = await future
            results.append([img_name, pred])
            print(f"{img_name} -> {pred}")

    # 寫入 CSV
    with open(OUTPUT_CSV, mode="w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["filename", "prediction"])
        writer.writerows(results)

    print(f"Batch prediction complete. Results saved to {OUTPUT_CSV}")

if __name__ == "__main__":
    asyncio.run(batch_predict())
