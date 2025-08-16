# run_yolo_small_cpu.py
import os
# ⬇️ 스레드/메모리 최소화: torch import 전에 설정
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

import torch
from PIL import Image
from pathlib import Path
from ultralytics import YOLO
from .image_utils import download_image

# === 경로 설정 ===
BASE_DIR = Path(__file__).resolve().parents[1]  
WEIGHTS_REL = Path("vision/models/lf-y8s-768-dv0-m1-fp32-pt-20250814.pt")  
MODEL_PATH = BASE_DIR / WEIGHTS_REL

# 가중치 존재 확인
if not MODEL_PATH.exists():
    raise FileNotFoundError(f"YOLO weights not found: {MODEL_PATH}")

# === 클래스 매핑 ===
item_dict = {
    0: "계산기", 1: "마우스", 2: "보조배터리", 3: "무선이어폰", 4: "스마트워치",
    5: "노트북", 6: "태블릿펜", 7: "태블릿", 8: "무선헤드폰", 9: "USB메모리",
    10: "휴대폰", 11: "무선이어폰크래들", 12: "반지", 13: "팔찌", 14: "목걸이",
    15: "귀걸이", 16: "아날로그손목시계", 17: "연필", 18: "볼펜", 19: "지우개",
    20: "필통", 21: "샤프", 22: "커터칼", 23: "샤프심통", 24: "자",
    25: "안경", 26: "캡/야구 모자", 27: "백팩", 28: "지갑",
}

# CPU 스레드 최소화 (추가)
torch.set_num_threads(1)
torch.set_num_interop_threads(1)

# === 모델 로드 ===
# Ultralytics는 device를 predict에서 지정하는 것으로 충분. .to("cpu") 생략 가능
model = YOLO(str(MODEL_PATH))

def _process_single_result(result):
    """
    Ultralytics Results -> list[dict]
    dict: { class_name, bbox[x1,y1,x2,y2], conf }
    """
    boxes = result.boxes.xyxy
    confidences = result.boxes.conf
    classes = result.boxes.cls

    # 텐서 → 리스트
    if isinstance(boxes, torch.Tensor): boxes = boxes.cpu().tolist()
    if isinstance(confidences, torch.Tensor): confidences = confidences.cpu().tolist()
    if isinstance(classes, torch.Tensor): classes = classes.cpu().tolist()

    outputs = []
    for box, conf, cls in zip(boxes, confidences, classes):
        cid = int(cls)  # ★ 정수 변환 중요
        name = item_dict.get(cid, f"unknown_{cid}")
        outputs.append({
            "class_id": cid,
            "class_name": name,
            "bbox": [float(x) for x in box],  # x1,y1,x2,y2
            "conf": float(conf),
        })
    return outputs

def predict_yolo(param: str, imgsz: int = 512, conf_thres: float = 0.25, iou_thres: float = 0.65):
    """
    이미지 경로를 넣으면 감지 결과를 리스트로 반환
    - t3.micro(1GB) 대응: imgsz<=512, batch=1, 스레드=1
    """
    # 경로 그대로 넘기는 게 메모리상 유리

    if isinstance(param, str) and param.startswith("http"):
        img = download_image(param)
    elif hasattr(param, "read"):
        img = Image.open(param).convert("RGB")
    else:
        raise ValueError("지원하지 않는 이미지 입력 형식입니다.")

    results = model.predict(
        source=img,
        imgsz=imgsz,
        device="cpu",
        conf=conf_thres,
        iou=iou_thres,
        verbose=False,
        save=False,
        stream=False,   # 리스트로 반환
        max_det=100
    )

    # results는 list[Results]
    aggregated = []
    for r in results:
        aggregated.extend(_process_single_result(r))
    return aggregated

if __name__ == "__main__":
    test_img = str(BASE_DIR / "apps" / "ai_gateway" / "samples" / "test.jpg")
    if not Path(test_img).exists():
        print(f"[warn] test image not found: {test_img}")
    else:
        preds = predict_yolo(test_img, imgsz=512, conf_thres=0.25, iou_thres=0.65)
        for p in preds:
            print(p)