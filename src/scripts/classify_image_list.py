import os
import shutil

# 🧾 아이디 → 클래스명 매핑
item_dict = {
    174: "계산기", 167: "마우스", 156: "보조배터리", 146: "무선이어폰", 150: "스마트워치",
    141: "노트북", 136: "태블릿펜", 131: "태블릿", 132: "무선헤드폰", 133: "USB메모리",
    126: "휴대폰", 127: "무선이어폰크래들", 276: "반지", 277: "팔찌", 278: "목걸이",
    279: "귀걸이", 280: "아날로그손목시계", 299: "연필", 300: "볼펜", 314: "지우개",
    317: "필통", 319: "샤프", 323: "커터칼", 324: "샤프심통", 328: "자", 457: "안경",
    464: "캡/야구 모자", 466: "백팩", 467: "지갑"
}

# 🧾 경로 설정
txt_file_path = "id_image_list_피혁_잡화.txt"
images_folder = r'C:\Users\user\Downloads\037.Small object detection을 위한 이미지 데이터\01.데이터\2.Validation\VS_피혁_잡화\mnt\nas2\Projects\TTA_2022_jgcha\jhbae\037.Small object detection을 위한 이미지 데이터\01.데이터\2.Validation\1.원천데이터\TL_피혁_잡화\leather01'
output_base_folder = "./sorted_images"  # 복사본이 들어갈 루트 폴더

# 🗂️ 출력 폴더 미리 생성
for category_name in set(item_dict.values()):
    target_dir = os.path.join(output_base_folder, category_name)
    os.makedirs(target_dir, exist_ok=True)

# 📄 텍스트 파일 읽기
with open(txt_file_path, 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        try:
            category_id_str, image_filename = line.split()
            category_id = int(category_id_str)

            # id → 클래스명 변환
            category_name = item_dict.get(category_id)
            if not category_name:
                print(f"[무시됨] 알 수 없는 ID: {category_id}")
                continue

            # 원본 이미지 경로 (.jpg라고 가정)
            src_image_path = os.path.join(images_folder, image_filename + ".jpg")

            if not os.path.exists(src_image_path):
                print(f"[❌ 없음] {src_image_path}")
                continue

            # 복사 대상 폴더
            dest_path = os.path.join(output_base_folder, category_name, image_filename + ".jpg")
            shutil.copy2(src_image_path, dest_path)
            print(f"[복사됨] {image_filename}.jpg → {category_name}/")

        except ValueError as e:
            print(f"[오류] 라인 파싱 실패: '{line}'")

print("\n✅ 이미지 정리가 완료되었습니다.")
