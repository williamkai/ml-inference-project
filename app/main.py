import warnings
warnings.filterwarnings(
    "ignore",
    message="enable_nested_tensor is True, but self.use_nested_tensor is False"
)

import zipfile
from typing import List, Dict
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from PIL import Image
from pydantic import BaseModel
import io
import os
import torch
import torchvision.transforms as transforms
from app.model import CNNTransformer

app = FastAPI(title="Digit Recognition API")

# 設定設備
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# 載入模型
model = CNNTransformer()
model.load_state_dict(torch.load("model_weights.pth", map_location=device))
model.to(device)
model.eval()

# 前處理
transform = transforms.Compose([
    transforms.Grayscale(num_output_channels=1),
    transforms.Resize((28, 28)),
    transforms.ToTensor(),
])

# 推論函式
def predict_image(image: Image.Image):
    tensor = transform(image).unsqueeze(0).to(device)# type: ignore
    with torch.no_grad():
        output = model(tensor)
        pred = torch.argmax(output, dim=1)
    return int(pred.item())

# Pydantic 回傳模型
class BatchPredictionResponse(BaseModel):
    predictions: Dict[str, int]

# 單張圖片 API
@app.post(
    "/predict",
    responses={
        400: {
            "description": "檔案格式錯誤或無法開啟圖片",
            "content": {
                "application/json": {
                    "example": {"error": "File is not an image: filename.png"}
                }
            },
        }
    },
)
async def predict(file: UploadFile = File(..., description="PNG/JPG/JPEG 上傳圖片")):
    """
    單張數字識別 API

    **功能說明：**
    - 預測單張手寫數字圖片
    - 目前僅支援 PNG / JPG / JPEG 格式

    **請求方式：**
    - POST /predict
    - Content-Type: multipart/form-data
    - 欄位名稱：`file` (上傳圖片檔案)

    **回傳格式：**
    ```json
    {
        "prediction": 7
    }
    ```

    **注意事項：**
    - 若檔案不是圖片格式，會回傳 400 錯誤
    - 圖片將自動轉灰階並縮放為 28x28 進行模型推論
    """
    filename = (file.filename or "").lower()
    if not filename.endswith((".png", ".jpg", ".jpeg")):
        return JSONResponse(
            content={"error": f"File is not an image: {file.filename}"},
            status_code=400,
        )

    try:
        content = await file.read()
        image = Image.open(io.BytesIO(content)).convert("L")
        pred = predict_image(image)
        return JSONResponse(content={"prediction": pred})
    except Exception as e:
        return JSONResponse(
            content={"error": f"Cannot open image {file.filename}: {str(e)}"},
            status_code=400,
        )


# 批次 API
@app.post(
    "/predict_batch",
    response_model=BatchPredictionResponse,
    responses={
        400: {
            "description": "檔案格式錯誤或無法開啟圖片",
            "content": {
                "application/json": {
                    "example": {"error": "Zip contains non-image file: filename.png"}
                }
            },
        }
    },
)
async def predict_batch(
    files: List[UploadFile] = File(
        ...,
        description=(
            "單張或多張圖片，或 ZIP 壓縮檔（僅包含圖片，可包含資料夾，隱藏檔或非圖片會回傳錯誤）"
        ),
    )
):
    """
    批次數字識別 API

    此 API 支援：
    - 單張圖片（PNG / JPG / JPEG）
    - 多張圖片（同時上傳多個檔案）
    - ZIP 壓縮檔（僅包含圖片，可包含資料夾，隱藏檔或非圖片會回傳錯誤）

    **請求方式：**
    - POST /predict_batch
    - Content-Type: multipart/form-data
    - 欄位名稱：`files` (可上傳多個檔案)
    
    **回傳格式：**
    ```json
    {
        "predictions": {
            "img1.png": 3,
            "img2.jpg": 7,
            "img3.png": 0
        }
    }
    ```

    **注意事項：**
    1. 非圖片檔案會回傳錯誤
    2. ZIP 壓縮檔中資料夾會自動處理，只解析圖片
    3. 隱藏系統資料夾（如 `.ipynb_checkpoints`）會自動忽略
    4. 目前僅支援 PNG / JPG / JPEG 格式
    """
    results = {}

    for file in files:
        filename = (file.filename or "").lower()
        content = await file.read()

        if filename.endswith(".zip"):
            try:
                z = zipfile.ZipFile(io.BytesIO(content))
            except zipfile.BadZipFile:
                return JSONResponse(
                    content={"error": f"Invalid zip file: {file.filename}"},
                    status_code=400
                )

            for name in z.namelist():
                # 忽略資料夾或隱藏系統資料夾
                if name.endswith("/") or ".ipynb_checkpoints" in name:
                    continue

                if not name.lower().endswith((".png", ".jpg", ".jpeg")):
                    return JSONResponse(
                        content={"error": f"Zip contains non-image file: {name}"},
                        status_code=400
                    )

                file_basename = os.path.basename(name)  # 只取檔名

                with z.open(name) as f:
                    try:
                        image = Image.open(f).convert("L")
                        results[file_basename] = predict_image(image)
                    except Exception as e:
                        return JSONResponse(
                            content={"error": f"Cannot open image {file_basename}: {str(e)}"},
                            status_code=400
                        )

        else:
            # 單張或多張圖片
            if not filename.endswith((".png", ".jpg", ".jpeg")):
                return JSONResponse(
                    content={"error": f"File is not an image: {file.filename}"},
                    status_code=400
                )
            try:
                image = Image.open(io.BytesIO(content)).convert("L")
                results[file.filename] = predict_image(image)
            except Exception as e:
                return JSONResponse(
                    content={"error": f"Cannot open image {file.filename}: {str(e)}"},
                    status_code=400
                )

    return JSONResponse(content={"predictions": results})