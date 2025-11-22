import warnings

# 只忽略 Transformer 層的 nested_tensor 警告
warnings.filterwarnings(
    "ignore",
    message="enable_nested_tensor is True, but self.use_nested_tensor is False"
)
import torch
from PIL import Image
import torchvision.transforms as transforms
from app.model import CNNTransformer

# 選擇運算設備：有 GPU 用 GPU，沒有就用 CPU
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# 載入模型
model = CNNTransformer()
model.load_state_dict(torch.load("model_weights.pth", map_location=device))
model.to(device)
model.eval()  # 設定模型為推論模式

# 前處理：確保輸入是灰階、28x28、轉成 Tensor
transform = transforms.Compose([
    transforms.Grayscale(num_output_channels=1),
    transforms.Resize((28, 28)),
    transforms.ToTensor(),
])

# 測試圖片
img = Image.open("ts_png/img_1_label_5.png").convert("L")  
tensor = transform(img).unsqueeze(0).to(device)  # [1,1,28,28]# type: ignore

# 推論
with torch.no_grad():
    output = model(tensor)
    pred = torch.argmax(output, dim=1)

print("Prediction:", pred.item())
