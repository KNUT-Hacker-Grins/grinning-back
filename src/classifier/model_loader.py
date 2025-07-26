import os
import torch
import threading
from torchvision import models, transforms
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = os.path.join(BASE_DIR, 'classifier', 'weights', 'resnet18_lostitem2.pth')
CLASS_NAMES = sorted(["휴대폰", "이어폰", "노트북", "시계", "지갑", "백팩", "우산"])
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

class ModelSingleton:
    _model = None
    _transform = None
    """
    한 스레드가 모델을 초기화하고 나면, 
    다른 스레드는 _model이 None이 아니므로 로딩을 건너뜁니다.
    즉, 모델은 딱 한 번만 안전하게 로딩됩니다.
    """
    _lock = threading.Lock()

    @classmethod
    def get_model(cls):
        with cls._lock:
            if cls._model is None:
                model = models.resnet18(pretrained=False)
                model.fc = torch.nn.Linear(model.fc.in_features, len(CLASS_NAMES))
                model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
                model = model.to(DEVICE)
                model.eval()
                cls._model = model
            return cls._model
            
    @classmethod
    def get_transform(cls):
        if cls._transform is None:
            cls._transform = transforms.Compose([
                transforms.Resize((224, 224)),               # 크기만 고정
                transforms.ToTensor(),                       # Tensor 변환
                transforms.Normalize([0.485, 0.456, 0.406],  # 정규화
                                    [0.229, 0.224, 0.225])
            ])
        return cls._transform