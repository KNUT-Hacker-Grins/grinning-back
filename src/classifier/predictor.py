import os
import torch
from PIL import Image
from pathlib import Path
from .image_utils import download_image
from .model_loader import ModelSingleton
from .error import ImageClassificationError

CATEGORY_MAP = {
    "전자제품": ["휴대폰", "이어폰", "노트북"],
    "패션": ["시계", "지갑", "백팩"],
    "기타": ["우산"]
}

CLASS_NAMES = sorted(["휴대폰", "이어폰", "노트북", "시계", "지갑", "백팩", "우산"])
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

THRESHOLD = 0.7

def predict_image(param):    
    try:
        # case 1: 이미지 링크 (str로 들어옴)
        if isinstance(param, str) and param.startswith("http"):
            img = download_image(param)

        # case 2: 파일 객체 (예: request.FILES['image'])
        elif hasattr(param, "read"):
            img = Image.open(param).convert("RGB")

        else:
            raise ValueError("지원하지 않는 이미지 입력 형식입니다.")
        
        img_t = ModelSingleton.get_transform()(img).unsqueeze(0).to(DEVICE)
        model = ModelSingleton.get_model()
        with torch.no_grad():
            output = model(img_t)
            prob = torch.nn.functional.softmax(output, dim=1)

            # pred_idx = prob.argmax().item()
            # confidence = prob[0, pred_idx].item()
            # pred_label = CLASS_NAMES[pred_idx]

            topk = torch.topk(prob, k=3)  
            topk_indices = topk.indices[0].tolist() 
            topk_probs = [f"{round(p, 4)*100}%" for p in topk.values[0].tolist()] 
            topk_labels = [CLASS_NAMES[i] for i in topk_indices]
            topk_categories = [category for label in topk_labels for category, items in CATEGORY_MAP.items() if label in items]

            # if confidence >= THRESHOLD:
            #     return {
            #         "label": pred_label,
            #         "confidence": round(confidence, 4),
            #         "status": "certain"
            #     }
            # else:
            #     return {
            #         "label": "unknown",
            #         "confidence": round(confidence, 4),
            #         "status": "uncertain"
            #     }

            return [
                {"category": category, "label": label, "confidence": prob}
                for category, label, prob in zip(topk_categories, topk_labels, topk_probs)
            ]
            
    except Exception as e:
        raise ImageClassificationError(f"이미지 분류 실패: {e}")
    
