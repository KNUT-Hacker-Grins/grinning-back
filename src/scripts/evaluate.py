import os 
import torch
import numpy as np
import torch.nn as nn
from pathlib import Path
from torch.utils.data import DataLoader
from torchvision import datasets, transforms, models
from sklearn.metrics import classification_report, confusion_matrix

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = os.path.join(BASE_DIR, 'classifier', 'data')

val_transform = transforms.Compose([
    transforms.Resize((224, 224)),                          # 고정 크기
    transforms.ToTensor(),                                  # Tensor 변환
    transforms.Normalize([0.485, 0.456, 0.406],             # 정규화
                         [0.229, 0.224, 0.225])
])  

test_dataset = datasets.ImageFolder(os.path.join(DATA_DIR, 'val'), transform=val_transform)
test_loader = DataLoader(test_dataset, batch_size=64, shuffle=False)

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model_dir = os.path.join(BASE_DIR, 'classifier', 'weights')
model_files = [f for f in os.listdir(model_dir) if f.endswith('.pt') or f.endswith('.pth')]
CLASS_NAMES = sorted(["휴대폰", "이어폰", "노트북", "시계", "지갑", "백팩", "우산"])

def evaluate_with_metrics(model, dataloader, device, class_names=None):
    model.to(device)
    model.eval()
    correct, total = 0, 0
    y_true, y_pred = [], []

    with torch.no_grad():
        for x, y in dataloader:
            x, y = x.to(device), y.to(device)
            out = model(x)
            preds = out.argmax(dim=1)

            correct += (preds == y).sum().item()
            total += y.size(0)

            y_true.extend(y.cpu().numpy())
            y_pred.extend(preds.cpu().numpy())

    acc = correct / total
    report = classification_report(y_true, y_pred, target_names=class_names, digits=4)
    cm = confusion_matrix(y_true, y_pred)

    return acc, report, cm


for model_file in model_files:
    model = models.resnet18(weights=None)        
    model.fc = nn.Linear(512, 7)                 

    model_path = os.path.join(model_dir, model_file)
    state_dict = torch.load(model_path, map_location=device)
    model.load_state_dict(state_dict)  

    acc, report, cm = evaluate_with_metrics(model, test_loader, device, class_names=CLASS_NAMES)
    print(f"정확도: {acc*100:.2f}%\n")
    print("🔍 분류 리포트:\n", report)
    print("🧮 Confusion Matrix:\n", cm)

