
import os
from PIL import Image
import pandas as pd

# 경로 설정
new_image_dir = "data/new_images"
split_dir = "data/split_images"
os.makedirs(split_dir, exist_ok=True)

# CSV 경로
pair_csv_path = "data/image_pairs.csv"
blind_csv_path = "data/blind_images.csv"

# 기존 CSV 불러오기 (없으면 빈 DataFrame 생성)
if os.path.exists(pair_csv_path):
    image_pairs = pd.read_csv(pair_csv_path)
else:
    image_pairs = pd.DataFrame(columns=["real_path", "virtual_path"])

if os.path.exists(blind_csv_path):
    blind_images = pd.read_csv(blind_csv_path)
else:
    blind_images = pd.DataFrame(columns=["image_path", "label"])

# 처리할 이미지 목록
for fname in os.listdir(new_image_dir):
    if not fname.lower().endswith((".png", ".jpg", ".jpeg")):
        continue

    base_name = os.path.splitext(fname)[0]
    left_path = f"data/split_images/{base_name}_left.png"
    right_path = f"data/split_images/{base_name}_right.png"

    # 중복된 경우 스킵
    if ((image_pairs["real_path"] == left_path) & (image_pairs["virtual_path"] == right_path)).any():
        continue

    # 분할
    try:
        img = Image.open(os.path.join(new_image_dir, fname))
        w, h = img.size
        left = img.crop((0, 0, w // 2, h))
        right = img.crop((w // 2, 0, w, h))
        left.save(left_path)
        right.save(right_path)

        # 실험 1용 추가
        image_pairs.loc[len(image_pairs)] = [left_path, right_path]

        # 실험 2용 추가
        blind_images.loc[len(blind_images)] = [left_path, "real"]
        blind_images.loc[len(blind_images)] = [right_path, "fake"]
    except Exception as e:
        print(f"Error processing {fname}: {e}")

# 저장
image_pairs.to_csv(pair_csv_path, index=False)
blind_images.to_csv(blind_csv_path, index=False)

print("✅ 이미지 분할 및 CSV 업데이트 완료!")
