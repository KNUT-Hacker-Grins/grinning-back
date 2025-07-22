import os
import torch
from .image_utils import download_image
from .model_loader import ModelSingleton
from pathlib import Path

BASE_DIR = str(Path(__file__).resolve().parent.parent.parent)

MODEL_PATH = os.path.join(BASE_DIR, 'lost_cls', 'resnet18_lostitem.pth')
DATA_DIR = os.path.join(BASE_DIR, 'lost_cls', 'data', 'train')
CLASS_NAMES = sorted(os.listdir(DATA_DIR))
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

def predict_image(image_url):    
    try:
        img = download_image(image_url)
        img_t = ModelSingleton.get_transform()(img).unsqueeze(0).to(DEVICE)
        model = ModelSingleton.get_model()
        with torch.no_grad():
            output = model(img_t)
            prob = torch.nn.functional.softmax(output, dim=1)
            print(prob)
            pred_idx = prob.argmax().item()
            pred_label = CLASS_NAMES[pred_idx]
            confidence = prob[0, pred_idx].item()
        return pred_label  # 카테고리만 반환
    except Exception as e:
        print(f"[Error] 이미지 분류 실패: {e}")
        return None  # 분류 실패 시 None 또는 'unknown' 등