import os
import torch
import threading
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = os.path.join(BASE_DIR, 'classifier', 'weights', 'resnet18_lostitem.pth')
CLASS_NAMES = sorted(["휴대폰", "이어폰", "노트북", "시계", "지갑", "백팩", "우산"])
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

class ModelSingleton:
    _model = None
    _transform = None
    _lock = threading.Lock()

    @classmethod
    def get_model(cls):
        with cls._lock:
            if cls._model is None:
                from torchvision import models  # lazy import
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
            from torchvision import transforms  # lazy import
            cls._transform = transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
            ])
        return cls._transform