import streamlit as st
import pandas as pd
import os
from PIL import Image
from save_to_gsheet import save_csv_to_sheet

# 경로 설정
PAIR_CSV = "data/image_pairs.csv"
BLIND_CSV = "data/blind_images.csv"
RESULT_DIR = "results"
# EX1_IMAGE_DIR = "/mnt/14T-2/ktmin/glomerulus_segmentation/inference_batch_save_mask_contour_binary/input/"
EX1_IMAGE_DIR = "data/task_1_glomerulus"
EX1_RESULT_PATH = os.path.join(RESULT_DIR, "results_ex1.csv")
EX2_RESULT_PATH = os.path.join(RESULT_DIR, "results_ex2.csv")

# 디렉토리 확인
os.makedirs(RESULT_DIR, exist_ok=True)

# 실험 1 이미지 리스트 불러오기
ex1_image_list = []
if os.path.isdir(EX1_IMAGE_DIR):
    for fname in sorted(os.listdir(EX1_IMAGE_DIR)):
        if fname.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tif', '.tiff')):
            ex1_image_list.append(os.path.join(EX1_IMAGE_DIR, fname))

# 사용자 정보 입력 (사이드바)
st.sidebar.title("사용자 정보 입력")
name = st.sidebar.text_input("이름을 입력해주세요.")
affiliation = st.sidebar.text_input("소속을 입력해주세요.")

if not name or not affiliation:
    st.warning("왼쪽 사이드바에서 이름과 소속을 모두 입력해 주세요.")
    st.stop()

# 세션 상태 초기화
if "ex1_index" not in st.session_state:
    st.session_state.ex1_index = 0
if "ex2_index" not in st.session_state:
    st.session_state.ex2_index = 0

# 데이터 로딩
try:
    image_pairs = pd.read_csv(PAIR_CSV)
    blind_images = pd.read_csv(BLIND_CSV)
except Exception as e:
    st.error(f"데이터 로딩 중 오류 발생: {e}")
    st.stop()

# UI 시작
st.title("병리학자 정성 평가 플랫폼")

tab1, tab2 = st.tabs(["실험 1: 병변(글로메룰루스) 존재 판별 (있다/없다)", "실험 2: 블라인드 테스트"])

# ---------------------
# 실험 1 (binary task)
# ---------------------
with tab1:
    st.header("실험 1: 병변(글로메룰루스) 존재 판별 (있다/없다)")
    idx = st.session_state.ex1_index
    if idx < len(ex1_image_list):
        img_path = ex1_image_list[idx]
        st.image(img_path, caption=f"이미지 {idx+1} / {len(ex1_image_list)}", use_container_width=True)
        answer = st.radio("이 이미지에 병변(글로메룰루스)이 있습니까?", ["있다", "없다"], horizontal=True)
        if st.button("제출 (실험 1)", key=f"submit_ex1_{idx}"):
            result = pd.DataFrame([{
                "evaluator": name,
                "affiliation": affiliation,
                "image_path": img_path,
                "answer": answer
            }])
            result.to_csv(EX1_RESULT_PATH, mode="a", header=not os.path.exists(EX1_RESULT_PATH), index=False)
            st.session_state.ex1_index += 1
            st.success("제출 완료! 다음 항목으로 이동.")
            st.stop()
    else:
        st.write(f"실험 1 이미지 폴더: {EX1_IMAGE_DIR}")
        st.write(f"이미지 개수: {len(ex1_image_list)}")
        if len(ex1_image_list) > 0:
            st.write("예시 파일:", ex1_image_list[:3])
        st.success("실험 1 평가가 완료되었습니다.")

# ---------------------
# 실험 2
# ---------------------
with tab2:
    st.header("실험 2: 블라인드 테스트 (실제 / 가상 맞히기)")
    idx = st.session_state.ex2_index
    if idx < len(blind_images):
        shuffled = blind_images.sample(frac=1, random_state=42).reset_index(drop=True)
        row = shuffled.iloc[idx]
        st.image(row["image_path"], caption="이 이미지는 실제일까요, 가상일까요?", use_container_width=True)

        prediction = st.radio("이 이미지의 정체는?", ["실제", "가상"], key=f"predict_{idx}")
        if st.button("제출 (실험 2)", key=f"submit_ex2_{idx}"):
            result = pd.DataFrame([{
                "evaluator": name,
                "affiliation": affiliation,
                "image_path": row["image_path"],
                "label": row["label"],
                "prediction": prediction
            }])
            result.to_csv(EX2_RESULT_PATH, mode="a", header=not os.path.exists(EX2_RESULT_PATH), index=False)
            st.session_state.ex2_index += 1
            st.success("제출 완료! 다음 항목으로 이동.")
            st.stop()
    else:
        st.success("실험 2 평가가 완료되었습니다.")

if (
    st.session_state.ex1_index >= len(ex1_image_list) and
    st.session_state.ex2_index >= len(blind_images) and
    not st.session_state.get("upload_done", False)
):
    save_csv_to_sheet("results/results_ex1.csv", "실험1결과")
    save_csv_to_sheet("results/results_ex2.csv", "실험2결과")
    st.session_state.upload_done = True
    st.success("✅ Google Sheets에 평가 결과가 자동 저장되었습니다!")