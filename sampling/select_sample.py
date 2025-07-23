import os
import pandas as pd
import random
import shutil

random.seed(42)

# 경로 및 샘플 개수 등 주요 상수 정의
SAMPLE_PATH = "/mnt/14T-2/ktmin/glomerulus_segmentation/inference_batch_save_mask_contour_binary/input/"
SAMPLE_DIR = "/workspace/evaluation_app/data/task_1_glomerulus"
SAMPLE_CSV_PATH = "/mnt/14T-2/ktmin/glomerulus_segmentation/inference_batch_save_mask_contour_binary/patch_binary.csv"
OUTPUT_CSV = "/workspace/evaluation_app/sampling/sampled_patches.csv"
SAMPLE_N = 20

# 염색 그룹별 키워드 정의
STAIN_GROUPS = {
    'HE': ['HE', 'H-E'],
    'PAS': ['PAS'],
    'AFOG': ['AFOG'],
    'P-M': ['P-M', 'MS', 'PAMS']
}


def read_patch_csv(csv_path):
    """패치 정보 CSV를 읽어 DataFrame으로 반환"""
    return pd.read_csv(csv_path)


def split_by_class(df):
    """DataFrame에서 positive/negative 리스트 분리"""
    pos_list = list(df[df['mask_binary'] == 1]["patch_name"])
    neg_list = list(df[df['mask_binary'] == 0]["patch_name"])
    return pos_list, neg_list


def classify_by_stain(file_list):
    """파일명에서 염색 정보를 추출해 dict로 분류"""
    stain_dict = {k: [] for k in STAIN_GROUPS.keys()}
    stain_dict['Others'] = []
    for filename in file_list:
        filename_upper = filename.upper()
        found = False
        for stain, keywords in STAIN_GROUPS.items():
            if any(kw in filename_upper for kw in keywords):
                stain_dict[stain].append(filename)
                found = True
                break
        if not found:
            stain_dict['Others'].append(filename)
    return stain_dict


def sample_by_stain(stain_dict, n, label):
    """각 염색별로 n개씩 랜덤 샘플링하여 리스트 반환"""
    sampled = []
    for stain, files in stain_dict.items():
        sample_files = random.sample(files, min(n, len(files)))
        for fname in sample_files:
            sampled.append({'patch_name': fname, 'stain': stain, 'class': label})
    return sampled


def save_samples_to_csv(sampled_rows, output_csv):
    """샘플 리스트를 DataFrame으로 변환 후 CSV로 저장"""
    df = pd.DataFrame(sampled_rows)
    df = df[['patch_name', 'stain', 'class']]
    df.to_csv(output_csv, index=False)
    print(f"\n샘플링 결과가 {output_csv}로 저장되었습니다. (총 {len(df)}개)")


def print_stain_stats(stain_dict, label):
    """염색별 분포 및 예시 출력"""
    print(f"\n[{label.capitalize()} samples]")
    for stain, files in stain_dict.items():
        print(f"{stain}: {len(files)}개")
        if len(files) > 0:
            print(f"  예시: {files[:3]}")


def copy_sampled_files_to_dir(csv_path, src_dir, dst_dir):
    """샘플링된 patch_name 파일들을 src_dir에서 dst_dir로 복사"""
    df = pd.read_csv(csv_path)
    patch_names = df['patch_name'].tolist()
    os.makedirs(dst_dir, exist_ok=True)
    copied, missing = 0, 0
    for fname in patch_names:
        src = os.path.join(src_dir, fname)
        dst = os.path.join(dst_dir, fname)
        if os.path.exists(src):
            shutil.copy2(src, dst)
            copied += 1
        else:
            print(f"[경고] 파일 없음: {src}")
            missing += 1
    print(f"\n복사 완료: {copied}개, 누락: {missing}개")


def main():
    # 1. CSV 파일에서 데이터 읽기
    df = read_patch_csv(SAMPLE_CSV_PATH)
    # 2. positive/negative 리스트 분리
    pos_list, neg_list = split_by_class(df)
    print(f"pos_list: {len(pos_list)}")
    print(f"neg_list: {len(neg_list)}")

    # 3. 염색별로 분류
    pos_by_stain = classify_by_stain(pos_list)
    neg_by_stain = classify_by_stain(neg_list)

    # 4. 염색별 통계 출력
    print("\n=== 염색별 분류 결과 ===")
    print_stain_stats(pos_by_stain, 'positive')
    print_stain_stats(neg_by_stain, 'negative')

    # 5. 전체 통계 출력
    total_pos = sum(len(files) for files in pos_by_stain.values())
    total_neg = sum(len(files) for files in neg_by_stain.values())
    print(f"\n총 Positive: {total_pos}개")
    print(f"총 Negative: {total_neg}개")
    print(f"총합: {total_pos + total_neg}개")
    print(f"원본 pos_list: {len(pos_list)}개")
    print(f"원본 neg_list: {len(neg_list)}개")
    print(f"분류된 총합: {total_pos + total_neg}개")
    if (len(pos_list) + len(neg_list)) == (total_pos + total_neg):
        print("분류 결과와 원본 개수 일치! ✅")
    else:
        print("⚠️ 분류 결과와 원본 개수 불일치!")

    # 6. 염색별로 positive/negative 각각 25개씩 샘플링
    sampled_rows = []
    sampled_rows.extend(sample_by_stain(pos_by_stain, SAMPLE_N, 'positive'))
    sampled_rows.extend(sample_by_stain(neg_by_stain, SAMPLE_N, 'negative'))

    # 7. 결과를 CSV로 저장
    save_samples_to_csv(sampled_rows, OUTPUT_CSV)

    # 8. 샘플링된 파일들을 SAMPLE_PATH에서 SAMPLE_DIR로 복사
    print(f"\n샘플링된 파일을 {SAMPLE_PATH} -> {SAMPLE_DIR}로 복사합니다...")
    copy_sampled_files_to_dir(OUTPUT_CSV, SAMPLE_PATH, SAMPLE_DIR)


if __name__ == "__main__":
    main()




