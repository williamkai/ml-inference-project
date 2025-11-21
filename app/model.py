import torch
import torch.nn as nn
import torch.nn.functional as F

class CNNTransformer(nn.Module):
    def __init__(self):
        super(CNNTransformer, self).__init__()

        # CNN 部分
        self.conv1 = nn.Conv2d(1, 32, 3, padding=1)
        self.conv2 = nn.Conv2d(32, 64, 3, padding=1)
        self.pool = nn.MaxPool2d(2, 2)

        # Transformer 部分
        self.linear_in = nn.Linear(14 * 14, 128)
        self.transformer_layer = nn.TransformerEncoderLayer(d_model=128, nhead=8)
        self.transformer = nn.TransformerEncoder(self.transformer_layer, num_layers=2)

        # 最後分類器
        self.fc = nn.Linear(64 * 128, 10)

    def forward(self, x):
        x = F.relu(self.conv1(x))
        x = F.relu(self.conv2(x))
        x = self.pool(x)  # [batch, 64, 14, 14]

        # 轉成 transformer token
        x = x.view(x.size(0), 64, -1)       # [batch, 64, 196]
        x = self.linear_in(x)               # [batch, 64, 128]
        x = x.permute(1, 0, 2)              # [seq_len=64, batch, 128]
        x = self.transformer(x)             # [64, batch, 128]
        x = x.permute(1, 0, 2)              # [batch, 64, 128]
        x = x.reshape(x.size(0), -1)        # [batch, 64*128]
        x = self.fc(x)                      # [batch, 10]
        return x
