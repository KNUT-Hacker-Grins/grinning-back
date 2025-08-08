import os
import torch
from pathlib import Path
from torch import nn, optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms, models

# 1. 하이퍼파라미터 세팅
# 내 환경으로는 16이 가장 안정적! 
# 에포크 수 변화 

BATCH_SIZE = 16
EPOCHS = 10
LR = 0.001
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = os.path.join(BASE_DIR, 'classifier', 'data')
NUM_CLASSES = len(os.listdir(os.path.join(DATA_DIR, 'train')))

"""
증강은 데이터가 적거나 편향되어 있을 때, "더 다양하고 일반화된 상황"을 가짜로 만들어서 모델이 더 똑똑해지도록 하는 과정입니다.
데이터가 부족할 때, 데이터가 편향되어 있을 때, 모델이 특정 특징에만 집착할 때

"""
# 2. 데이터 전처리 및 DataLoader
# 기본 입력 이미지 사이즈는 224x224
train_transform = transforms.Compose([
    transforms.RandomResizedCrop(224, scale=(0.8, 1.0)),  
    transforms.RandomHorizontalFlip(),                    
    transforms.RandomRotation(degrees=15),                
    transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),
    transforms.RandomAffine(
        degrees=10,
        translate=(0.1, 0.1),
        scale=(0.9, 1.1)
    ),                                                 
    transforms.ToTensor(),                                
    transforms.Normalize([0.485, 0.456, 0.406],             
                         [0.229, 0.224, 0.225]),
    transforms.RandomErasing(p=0.2)                        
])
val_transform = transforms.Compose([
    transforms.Resize(256),                                
    transforms.CenterCrop(224),                            
    transforms.ToTensor(),                                  
    transforms.Normalize([0.485, 0.456, 0.406],            
                         [0.229, 0.224, 0.225])
])  

train_data = datasets.ImageFolder(os.path.join(DATA_DIR, 'train'), transform=train_transform)
val_data = datasets.ImageFolder(os.path.join(DATA_DIR, 'val'), transform=val_transform)

train_loader = DataLoader(train_data, batch_size=BATCH_SIZE, shuffle=True)
val_loader = DataLoader(val_data, batch_size=BATCH_SIZE, shuffle=False)

# 3. 모델 준비 (ResNet18, 파인튜닝)
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model = models.resnet18(pretrained=True)
model.fc = nn.Linear(model.fc.in_features, NUM_CLASSES)
model = model.to(device)

criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=LR)

# 4. 학습 루프
for epoch in range(EPOCHS):
    model.train()
    running_loss = 0.0
    correct = 0
    total = 0
    for imgs, labels in train_loader:
        imgs, labels = imgs.to(device), labels.to(device)
        optimizer.zero_grad()
        outputs = model(imgs)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        running_loss += loss.item() * imgs.size(0)
        _, predicted = outputs.max(1)
        correct += predicted.eq(labels).sum().item()
        total += imgs.size(0)
    train_loss = running_loss / total
    train_acc = correct / total

    # 검증
    model.eval()
    val_loss = 0.0
    val_correct = 0
    val_total = 0
    with torch.no_grad():
        for imgs, labels in val_loader:
            imgs, labels = imgs.to(device), labels.to(device)
            outputs = model(imgs)
            loss = criterion(outputs, labels)
            val_loss += loss.item() * imgs.size(0)
            _, predicted = outputs.max(1)
            val_correct += predicted.eq(labels).sum().item()
            val_total += imgs.size(0)
    val_loss /= val_total
    val_acc = val_correct / val_total

    print(f"[Epoch {epoch+1}] Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.4f} | Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.4f}")

# 5. 모델 저장
torch.save(model.state_dict(), 'src/classifier/weights/resnet18_lostitem3.pth')
print("모델 저장 완료: resnet18_lostitem3.pth")
