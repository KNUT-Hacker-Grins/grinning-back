import os
import torch
from PIL import Image
from pathlib import Path
from .image_utils import download_image
from .error import ImageClassificationError

CATEGORY_MAP = {
    "전자제품": ["휴대폰", "이어폰", "노트북"],
    "패션": ["시계", "지갑", "백팩"],
    "기타": ["우산"]
}

CLASS_NAMES = sorted(["휴대폰", "이어폰", "노트북", "시계", "지갑", "백팩", "우산"])
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
THRESHOLD = 0.7

_model_singleton = None  # lazy load 객체 참조용


def get_model_singleton():
    global _model_singleton
    if _model_singleton is None:
        from . import model_loader
        _model_singleton = model_loader.ModelSingleton
    return _model_singleton


def predict_image(param):
    try:
        if isinstance(param, str) and param.startswith("http"):
            img = download_image(param)
        elif hasattr(param, "read"):
            img = Image.open(param).convert("RGB")
        else:
            raise ValueError("지원하지 않는 이미지 입력 형식입니다.")

        ms = get_model_singleton()
        img_t = ms.get_transform()(img).unsqueeze(0).to(DEVICE)
        model = ms.get_model()

        with torch.no_grad():
            output = model(img_t)
            prob = torch.nn.functional.softmax(output, dim=1)
            topk = torch.topk(prob, k=3)
            topk_indices = topk.indices[0].tolist()
            topk_probs = [f"{round(p, 4) * 100}%" for p in topk.values[0].tolist()]
            topk_labels = [CLASS_NAMES[i] for i in topk_indices]
            topk_categories = [category for label in topk_labels for category, items in CATEGORY_MAP.items() if label in items]

            return [
                {"category": category, "label": label, "confidence": prob}
                for category, label, prob in zip(topk_categories, topk_labels, topk_probs)
            ]

    except Exception as e:
        raise ImageClassificationError(f"이미지 분류 실패: {e}")
