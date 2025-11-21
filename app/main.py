from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from PIL import Image
import io
import torch
import torchvision.transforms as transforms
from model import CNNTransformer

app = FastAPI(title="Digit Recognition API")

# 載入模型
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = CNNTransformer()
model.load_state_dict(torch.load("model_weights.pth", map_location=device))
model.to(device)
model.eval()

# 圖片轉 tensor
transform = transforms.Compose([
    transforms.Resize((28, 28)),
    transforms.ToTensor(),
])

def predict_image(image: Image.Image):
    img_tensor = transform(image).unsqueeze(0).to(device)  # [1,1,28,28]
    with torch.no_grad():
        output = model(img_tensor)
        pred = torch.argmax(output, dim=1)
    return int(pred.item())

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    content = await file.read()
    image = Image.open(io.BytesIO(content)).convert("L")  # 灰階
    pred = predict_image(image)
    return JSONResponse(content={"prediction": pred})
