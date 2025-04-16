
import streamlit as st
import pandas as pd
import os
from PIL import Image

# 경로 설정
PAIR_CSV = "data/image_pairs.csv"
BLIND_CSV = "data/blind_images.csv"
RESULT_DIR = "results"
EX1_RESULT_PATH = os.path.join(RESULT_DIR, "results_ex1.csv")
EX2_RESULT_PATH = os.path.join(RESULT_DIR, "results_ex2.csv")

# 디렉토리 확인
os.makedirs(RESULT_DIR, exist_ok=True)

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
image_pairs = pd.read_csv(PAIR_CSV)
blind_images = pd.read_csv(BLIND_CSV)

# UI 시작
st.title("병리학자 정성 평가 플랫폼")

tab1, tab2 = st.tabs(["실험 1: 5점 척도 + 코멘트", "실험 2: 블라인드 테스트"])

# ---------------------
# 실험 1
# ---------------------
with tab1:
    st.header("실험 1: 유사성 평가 (1~5점 + 코멘트)")
    idx = st.session_state.ex1_index
    if idx < len(image_pairs):
        row = image_pairs.iloc[idx]
        col1, col2 = st.columns(2)
        with col1:
            st.image(row["real_path"], caption="실제 이미지", use_container_width=True)
        with col2:
            st.image(row["virtual_path"], caption="가상 이미지", use_container_width=True)

        score = st.radio("유사성 점수 (1=전혀 유사하지 않음, 5=매우 유사함)", [1, 2, 3, 4, 5], horizontal=True)
        comment = st.text_area("판단 근거 또는 코멘트 (선택 사항)", key=f"comment_{idx}")
        if st.button("제출 (실험 1)", key=f"submit_ex1_{idx}"):
            result = pd.DataFrame([{
                "evaluator": name,
                "affiliation": affiliation,
                "real_path": row["real_path"],
                "virtual_path": row["virtual_path"],
                "score": score,
                "comment": comment
            }])
            if os.path.exists(EX1_RESULT_PATH):
                result.to_csv(EX1_RESULT_PATH, mode="a", header=False, index=False)
            else:
                result.to_csv(EX1_RESULT_PATH, index=False)
            st.session_state.ex1_index += 1
            st.experimental_rerun()
    else:
        st.success("실험 1 평가가 완료되었습니다.")

# ---------------------
# 실험 2
# ---------------------
with tab2:
    st.header("실험 2: 블라인드 테스트 (실제 / 가상 맞히기)")
    idx = st.session_state.ex2_index
    if idx < len(blind_images):
        # row = blind_images.sample(frac=1, random_state=42).iloc[idx]
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
            if os.path.exists(EX2_RESULT_PATH):
                result.to_csv(EX2_RESULT_PATH, mode="a", header=False, index=False)
            else:
                result.to_csv(EX2_RESULT_PATH, index=False)
            st.session_state.ex2_index += 1
            st.experimental_rerun()
    else:
        st.success("실험 2 평가가 완료되었습니다.")
