import warnings

# 只忽略 Transformer 層的 nested_tensor 警告
warnings.filterwarnings(
    "ignore",
    message="enable_nested_tensor is True, but self.use_nested_tensor is False"
)


from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from PIL import Image
import io
import torch
import torchvision.transforms as transforms
from app.model import CNNTransformer

app = FastAPI(title="Digit Recognition API")

# 1️⃣ 設定設備
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# 2️⃣ 載入模型
model = CNNTransformer()
model.load_state_dict(torch.load("model_weights.pth", map_location=device))
model.to(device)
model.eval()

# 3️⃣ 前處理
transform = transforms.Compose([
    transforms.Grayscale(num_output_channels=1),
    transforms.Resize((28, 28)),
    transforms.ToTensor(),
])

# 4️⃣ 推論函式
def predict_image(image: Image.Image):
    tensor = transform(image).unsqueeze(0).to(device)  # type: ignore
    with torch.no_grad():
        output = model(tensor)
        pred = torch.argmax(output, dim=1)
    return int(pred.item())

# 5️⃣ API 路由
@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    content = await file.read()
    image = Image.open(io.BytesIO(content)).convert("L")
    pred = predict_image(image)
    return JSONResponse(content={"prediction": pred})
