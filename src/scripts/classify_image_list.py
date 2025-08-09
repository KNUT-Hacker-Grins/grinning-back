import os
import json

# YOLO 클래스 ID ↔️ 한글 클래스 이름
item_dict = {
    174: "계산기", 167: "마우스", 156: "보조배터리", 146: "무선이어폰", 150: "스마트워치",
    141: "노트북", 136: "태블릿펜", 131: "태블릿", 132: "무선헤드폰", 133: "USB메모리",
    126: "휴대폰", 127: "무선이어폰크래들", 276: "반지", 277: "팔찌", 278: "목걸이",
    279: "귀걸이", 280: "아날로그손목시계", 299: "연필", 300: "볼펜", 314: "지우개",
    317: "필통", 319: "샤프", 323: "커터칼", 324: "샤프심통", 328: "자", 457: "안경",
    464: "캡/야구 모자", 466: "백팩", 467: "지갑"
}

# 경로 설정
# target_list_path = './id_image_list_보석_귀금속_시계.txt' 
# json_folder = r'C:\Users\user\Downloads\037.Small object detection을 위한 이미지 데이터\01.데이터\2.Validation\VL_보석_귀금속_시계\mnt\nas2\Projects\TTA_2022_jgcha\jhbae\037.Small object detection을 위한 이미지 데이터\01.데이터\2.Validation\2.라벨링데이터\VL_보석_귀금속_시계\jewlery01'

target_list_path = './id_image_list_문구류.txt' 
json_folder = r'C:\Users\user\Downloads\037.Small object detection을 위한 이미지 데이터\01.데이터\2.Validation\VL_문구류\mnt\nas2\Projects\TTA_2022_jgcha\jhbae\037.Small object detection을 위한 이미지 데이터\01.데이터\2.Validation\2.라벨링데이터\VL_문구류\stationary01'

# target_list_path = './id_image_list_전자기기.txt' 
# json_folder = r'C:\Users\user\Downloads\037.Small object detection을 위한 이미지 데이터\01.데이터\2.Validation\VL_전자기기\mnt\nas2\Projects\TTA_2022_jgcha\jhbae\037.Small object detection을 위한 이미지 데이터\01.데이터\2.Validation\2.라벨링데이터\VL_전자기기\electronics01'

# target_list_path = './id_image_list_피혁_잡화.txt' 
# json_folder = r'C:\Users\user\Downloads\037.Small object detection을 위한 이미지 데이터\01.데이터\2.Validation\VL_피혁_잡화\mnt\nas2\Projects\TTA_2022_jgcha\jhbae\037.Small object detection을 위한 이미지 데이터\01.데이터\2.Validation\2.라벨링데이터\VL_피혁_잡화\leather01'

# 📄 대상 파일명 목록 불러오기 (확장자 없음)
with open(target_list_path, 'r', encoding='utf-8') as f:
    target_files = [line.strip().split()[1] for line in f if line.strip()]

print(f"[INFO] 총 {len(target_files)}개 JSON 라벨링 처리 시작")

# 전체 대상 처리
for basename in target_files:
    json_path = os.path.join(json_folder, basename + ".json")
    if not os.path.exists(json_path):
        print(f"[⚠️ 없음] {json_path}")
        continue

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    image_info = data.get("images", [{}])[0]
    ann_list = data.get("annotations", [])

    img_w = image_info.get("width")
    img_h = image_info.get("height")
    if not (img_w and img_h):
        print(f"[무시됨] {basename}.json → 이미지 크기 없음")
        continue

    # 클래스 ID 추출 (첫 항목 기준)
    if not ann_list:
        print(f"[무시됨] {basename}.json → bbox 없음")
        continue

    for ann in ann_list:
        category_id = ann.get("category_id")
        bbox = ann.get("bbox")

        if category_id not in item_dict or not bbox:
            print(f"[무시됨] {basename}.json → 알 수 없는 클래스 ID: {category_id}")
            continue

        class_name = item_dict[category_id]

        x, y, w, h = bbox
        x_center = (x + w / 2) / img_w
        y_center = (y + h / 2) / img_h
        w_norm = w / img_w
        h_norm = h / img_h

        yolo_line = f"{category_id} {x_center:.6f} {y_center:.6f} {w_norm:.6f} {h_norm:.6f}\n"

        yolo_txt_path = os.path.join("./sorted_images", str(item_dict[category_id]), basename + ".txt")

        with open(yolo_txt_path, 'w', encoding='utf-8') as out:
            out.write(yolo_line)

    print(f"[✅ 완료] {basename}.json → {class_name}/{basename}.txt")

print("\n🎉 지정된 JSON 파일만 YOLO 포맷으로 변환 완료!")
