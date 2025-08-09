import os
import json

item_dict = {
    174: "계산기",
    167: "마우스",
    156: "보조배터리",
    146: "무선이어폰",
    150: "스마트워치",
    141: "노트북",
    136: "태블릿펜",
    131: "태블릿",
    132: "무선헤드폰",
    133: "USB메모리",
    126: "휴대폰",
    127: "무선이어폰크래들",

    276: "반지",
    277: "팔찌",
    278: "목걸이",
    279: "귀걸이",
    280: "아날로그손목시계",

    299: "연필",
    300: "볼펜",
    314: "지우개",
    317: "필통",
    319: "샤프",
    323: "커터칼",
    324: "샤프심통",
    328: "자",

    457: "안경",
    464: "캡/야구 모자",
    466: "백팩",
    467: "지갑"
}

# 🔧 경로 설정 (현재 스크립트 기준 상대경로 또는 절대경로)
json_folder = r'C:\Users\user\Downloads\037.Small object detection을 위한 이미지 데이터\01.데이터\2.Validation\VL_피혁_잡화\mnt\nas2\Projects\TTA_2022_jgcha\jhbae\037.Small object detection을 위한 이미지 데이터\01.데이터\2.Validation\2.라벨링데이터\VL_피혁_잡화\leather01'
output_file = './id_image_list_피혁_잡화.txt' 

# 📝 결과 저장용 리스트
all_ids = []

# 📁 폴더 내 모든 JSON 파일 순회
for filename in os.listdir(json_folder):
    if filename.endswith('.json'):
        file_path = os.path.join(json_folder, filename)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # 📌 'id' 키가 존재할 경우에만 저장
                for annotation in data['annotations']:
                    category_id = annotation.get('category_id')
                    if category_id in item_dict:
                        print(f"✔️ category_id {category_id}: {item_dict[category_id]}")
                        all_ids.append([category_id, annotation.get('image_id')])
                    else:
                        print(f"❌ category_id {category_id}는 item_dict에 없음")
        except Exception as e:
            print(f"[오류] {filename} 처리 중 문제 발생: {e}")

# 📤 결과를 txt 파일로 저장
with open(output_file, 'w', encoding='utf-8') as f:
    for item_id in all_ids:
        f.write(str(item_id[0]) +' ' + item_id[1] + '\n')

print(f"✅ 총 {len(all_ids)}개의 id가 '{output_file}'에 저장되었습니다.")
