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
if "ex1_answers" not in st.session_state:
    st.session_state.ex1_answers = {}

# 데이터 로딩 (실험 2 관련 부분 주석 처리)
# try:
#     image_pairs = pd.read_csv(PAIR_CSV)
#     blind_images = pd.read_csv(BLIND_CSV)
# except Exception as e:
#     st.error(f"데이터 로딩 중 오류 발생: {e}")
#     st.stop()

# UI 시작
st.title("병리학자 정성 평가 플랫폼")

# tab1, tab2 = st.tabs(["실험 1: 병변(글로메룰루스) 존재 판별 (있다/없다)", "실험 2: 블라인드 테스트"])[0]
tab1 = st.tabs(["실험 1: 병변(글로메룰루스) 존재 판별 (있다/없다)"])[0]

# ---------------------
# 실험 1 (binary task) - 10장씩 보여주기
# ---------------------
with tab1:
    st.header("실험 1: 병변(글로메룰루스) 존재 판별 (있다/없다)")
    
    # 한 번에 보여줄 이미지 개수
    BATCH_SIZE = 10
    start_idx = st.session_state.ex1_index * BATCH_SIZE
    end_idx = min(start_idx + BATCH_SIZE, len(ex1_image_list))
    
    if start_idx < len(ex1_image_list):
        st.write(f"**이미지 {start_idx + 1} ~ {end_idx} / 총 {len(ex1_image_list)}장**")
        st.write("각 이미지에 대해 '있다' 또는 '없다'를 선택해주세요.")
        
        # 10장씩 이미지와 선택 옵션 표시
        for i in range(start_idx, end_idx):
            img_path = ex1_image_list[i]
            img_key = f"img_{i}"
            answer_key = f"answer_{i}"
            
            # 이미지와 선택 옵션을 같은 행에 배치
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # 이미지 사이즈를 줄이기 위해 width 파라미터 추가
                st.image(img_path, caption=f"이미지 {i + 1}", use_container_width=False, width=300)
            
            with col2:
                # 이전에 선택한 답이 있으면 그 값을 사용, 없으면 기본값
                default_answer = st.session_state.ex1_answers.get(answer_key, "있다")
                answer = st.radio(
                    f"이미지 {i + 1}의 답변:",
                    ["있다", "없다"],
                    key=answer_key,
                    index=0 if default_answer == "있다" else 1,
                    horizontal=True
                )
                # 답변을 세션에 저장
                st.session_state.ex1_answers[answer_key] = answer
        
        # 이전/다음 버튼 배치
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            # 이전 버튼 (첫 번째 배치가 아닐 때만 표시)
            if st.session_state.ex1_index > 0:
                if st.button("이전", key=f"prev_batch_{st.session_state.ex1_index}"):
                    st.session_state.ex1_index -= 1
                    st.rerun()
        
        with col2:
            # 빈 공간 (중앙 정렬을 위해)
            pass
        
        with col3:
            # 다음 버튼
            if st.button("다음", key=f"submit_batch_{st.session_state.ex1_index}"):
                # 현재 배치의 모든 답변을 저장 (덮어쓰기)
                for i in range(start_idx, end_idx):
                    answer_key = f"answer_{i}"
                    img_path = ex1_image_list[i]
                    answer = st.session_state.ex1_answers.get(answer_key, "있다")
                    
                    # 기존 결과에서 같은 이미지가 있으면 제거 (덮어쓰기)
                    if os.path.exists(EX1_RESULT_PATH):
                        existing_results = pd.read_csv(EX1_RESULT_PATH)
                        existing_results = existing_results[existing_results['image_path'] != img_path]
                        existing_results.to_csv(EX1_RESULT_PATH, index=False)
                    
                    result = pd.DataFrame([{
                        "evaluator": name,
                        "affiliation": affiliation,
                        "image_path": img_path,
                        "answer": answer
                    }])
                    result.to_csv(EX1_RESULT_PATH, mode="a", header=not os.path.exists(EX1_RESULT_PATH), index=False)
                
                # 다음 배치로 이동
                st.session_state.ex1_index += 1
                st.rerun()
            
    else:
        st.write(f"실험 1 이미지 폴더: {EX1_IMAGE_DIR}")
        st.write(f"이미지 개수: {len(ex1_image_list)}")
        if len(ex1_image_list) > 0:
            st.write("예시 파일:", ex1_image_list[:3])
        st.success("실험 1 평가가 완료되었습니다.")