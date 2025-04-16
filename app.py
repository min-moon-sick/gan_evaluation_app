
import streamlit as st
import pandas as pd
import os
from PIL import Image

# 데이터 불러오기
image_pairs = pd.read_csv("data/image_pairs.csv")
blind_images = pd.read_csv("data/blind_images.csv")

# 결과 저장 폴더
os.makedirs("results", exist_ok=True)
ex1_result_path = "results/results_ex1.csv"
ex2_result_path = "results/results_ex2.csv"

# 세션 상태 초기화
if "ex1_index" not in st.session_state:
    st.session_state.ex1_index = 0
if "ex2_index" not in st.session_state:
    st.session_state.ex2_index = 0

st.title("병리학적 정성 평가 플랫폼")

tab1, tab2 = st.tabs(["실험 1: 5점 척도 + 코멘트", "실험 2: 블라인드 테스트"])

with tab1:
    st.header("실험 1: 유사성 평가")
    if st.session_state.ex1_index < len(image_pairs):
        row = image_pairs.iloc[st.session_state.ex1_index]
        col1, col2 = st.columns(2)
        with col1:
            st.image(row["real_path"], caption="실제 이미지", use_column_width=True)
        with col2:
            st.image(row["virtual_path"], caption="가상 이미지", use_column_width=True)
        score = st.radio("유사성 점수 (1=전혀 유사하지 않음, 5=매우 유사함)", [1, 2, 3, 4, 5], horizontal=True)
        comment = st.text_area("판단 근거 또는 코멘트 (선택 사항)")
        if st.button("다음 (실험 1)"):
            result_df = pd.DataFrame([{
                "real_path": row["real_path"],
                "virtual_path": row["virtual_path"],
                "score": score,
                "comment": comment
            }])
            if os.path.exists(ex1_result_path):
                result_df.to_csv(ex1_result_path, mode="a", header=False, index=False)
            else:
                result_df.to_csv(ex1_result_path, index=False)
            st.session_state.ex1_index += 1
            st.experimental_rerun()
    else:
        st.success("실험 1 평가가 완료되었습니다.")

with tab2:
    st.header("실험 2: 블라인드 테스트")
    if st.session_state.ex2_index < len(blind_images):
        row = blind_images.sample(frac=1, random_state=42).iloc[st.session_state.ex2_index]
        st.image(row["image_path"], caption="이 이미지는 실제일까요? 가상일까요?", use_column_width=True)
        prediction = st.radio("이 이미지의 정체는?", ["실제", "가상"])
        if st.button("다음 (실험 2)"):
            result_df = pd.DataFrame([{
                "image_path": row["image_path"],
                "label": row["label"],
                "prediction": prediction
            }])
            if os.path.exists(ex2_result_path):
                result_df.to_csv(ex2_result_path, mode="a", header=False, index=False)
            else:
                result_df.to_csv(ex2_result_path, index=False)
            st.session_state.ex2_index += 1
            st.experimental_rerun()
    else:
        st.success("실험 2 평가가 완료되었습니다.")
