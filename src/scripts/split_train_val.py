import os
import shutil
import random

# 📁 입력 폴더
source_root = "./sorted_images"

# 📁 출력 폴더
train_root = "./dataset/train"
val_root = "./dataset/val"

# ⚙️ 설정
train_ratio = 0.8  # 8:2 비율

# ✅ 클래스별 순회
for class_name in os.listdir(source_root):
    class_path = os.path.join(source_root, class_name)
    if not os.path.isdir(class_path):
        continue

    # 📦 이미지 파일 수집
    images = [f for f in os.listdir(class_path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    random.shuffle(images)  # 셔플

    # ✂️ 분할
    split_idx = int(len(images) * train_ratio)
    train_images = images[:split_idx]
    val_images = images[split_idx:]

    # 📁 출력 폴더 생성
    os.makedirs(os.path.join(train_root, class_name), exist_ok=True)
    os.makedirs(os.path.join(val_root, class_name), exist_ok=True)

    # 📤 복사
    for img in train_images:
        shutil.copy2(
            os.path.join(class_path, img),
            os.path.join(train_root, class_name, img)
        )

    for img in val_images:
        shutil.copy2(
            os.path.join(class_path, img),
            os.path.join(val_root, class_name, img)
        )

    print(f"[✅ 분할 완료] {class_name}: Train={len(train_images)}, Val={len(val_images)}")

print("\n🎉 전체 데이터셋 분할 완료!")
