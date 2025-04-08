import streamlit as st
import pandas as pd
import os
import time
from datetime import datetime
import threading

# 모듈 임포트
from quiz_manager import QuizManager
from api_client import APIClient
from scoring import Scorer
from leaderboard_manager import LeaderboardManager
from logger import QuizLogger
import utils

# Set page title and configuration
st.set_page_config(
    page_title="3kingdoms Quiz Leaderboard",
    page_icon="🏆",
    layout="wide"
)

# 데이터 경로 설정
DATA_DIR = "data"
QUIZ_DATA_PATH = os.path.join(DATA_DIR, "quiz_data.csv")
LEADERBOARD_PATH = os.path.join(DATA_DIR, "leaderboard.csv")

# 디렉토리 생성
os.makedirs(DATA_DIR, exist_ok=True)

# 전역 객체 초기화
@st.cache_resource
def init_resources():
    quiz_manager = QuizManager(QUIZ_DATA_PATH)
    leaderboard_manager = LeaderboardManager(LEADERBOARD_PATH)
    scorer = Scorer()
    logger = QuizLogger()
    return quiz_manager, leaderboard_manager, scorer, logger

quiz_manager, leaderboard_manager, scorer, logger = init_resources()

# Function to load the leaderboard data
def load_leaderboard():
    return pd.read_csv(LEADERBOARD_PATH)

# Function to save the leaderboard data
def save_leaderboard(df):
    df.to_csv(LEADERBOARD_PATH, index=False)

# Main title
st.title("🏆 3kingdoms Quiz Leaderboard")
st.markdown("삼국지 퀴즈 API 리더보드 - 당신의 API 엔드포인트를 제출하고 성능을 확인하세요!")

# Create tabs for viewing and adding entries
tab1, tab2, tab3 = st.tabs(["리더보드", "API 제출", "진행 상황 모니터링"])

with tab1:
    st.header("현재 리더보드")
    
    # Load and display the leaderboard
    leaderboard_df = leaderboard_manager.get_leaderboard()
    
    # 필터링 옵션들
    col1, col2 = st.columns([3, 1])
    with col2:
        show_completed_only = st.checkbox("완료된 항목만 표시", value=True)
        deduplicate_names = st.checkbox("이름별 최고 성능만 표시", value=False)
        
        if deduplicate_names:
            dedup_metric = st.radio("중복 제거 기준:", 
                                   ["정확도 (correct_answer_rate)", 
                                    "LLM 점수 (llm_judge_result)"])
    
    # 필터링 적용
    if not leaderboard_df.empty:
        # 완료된 항목만 표시
        if show_completed_only:
            leaderboard_df = leaderboard_df[leaderboard_df["status"] == "completed"]
        
        # 이름 중복 제거
        if deduplicate_names and not leaderboard_df.empty:
            # 수치형으로 변환
            leaderboard_df["correct_answer_rate"] = pd.to_numeric(leaderboard_df["correct_answer_rate"], errors='coerce')
            leaderboard_df["llm_judge_result"] = pd.to_numeric(leaderboard_df["llm_judge_result"], errors='coerce')
            
            if dedup_metric == "정확도 (correct_answer_rate)":
                # 각 이름별로 정확도가 가장 높은 행만 선택
                idx = leaderboard_df.groupby('name')['correct_answer_rate'].idxmax()
                leaderboard_df = leaderboard_df.loc[idx]
            else:
                # 각 이름별로 LLM 점수가 가장 높은 행만 선택
                idx = leaderboard_df.groupby('name')['llm_judge_result'].idxmax()
                leaderboard_df = leaderboard_df.loc[idx]
        
        # 데이터 형식 지정 (표시용)
        display_df = leaderboard_df.copy()
        if "correct_answer_rate" in display_df.columns:
            display_df["correct_answer_rate"] = display_df["correct_answer_rate"].apply(
                lambda x: f"{float(x):.2f}%" if pd.notna(x) else "N/A"
            )
        if "average_response_time" in display_df.columns:
            display_df["average_response_time"] = display_df["average_response_time"].apply(
                lambda x: f"{float(x):.2f}초" if pd.notna(x) else "N/A"
            )
        
        # 데이터프레임 표시 (Streamlit의 기본 정렬 기능 활용)
        st.dataframe(display_df, use_container_width=True)
    else:
        st.info("아직 리더보드에 항목이 없습니다. 'API 제출' 탭에서 추가해보세요.")

with tab2:
    st.header("API 엔드포인트 제출")
    
    with st.form("submit_api_form"):
        name = st.text_input("이름")
        api_endpoint = st.text_input("API 엔드포인트 URL")
        
        submitted = st.form_submit_button("제출")
        
        if submitted:
            if name and api_endpoint:
                # 입력값 정제
                name = utils.sanitize_input(name)
                api_endpoint = utils.sanitize_input(api_endpoint)
                
                # 리더보드에 새 항목 추가
                success = leaderboard_manager.add_new_submission(name, api_endpoint)
                
                if success:
                    st.success(f"{name}님의 API가 제출되었습니다. 퀴즈 처리가 시작됩니다.")
                    
                    # 백그라운드에서 퀴즈 처리 시작
                    thread = threading.Thread(
                        target=process_quiz,
                        args=(name, api_endpoint)
                    )
                    thread.daemon = True
                    thread.start()
                else:
                    st.error("제출 중 오류가 발생했습니다. 다시 시도해주세요.")
            else:
                st.warning("이름과 API 엔드포인트를 모두 입력해주세요.")

with tab3:
    st.header("퀴즈 진행 상황 모니터링")
    
    # 진행 중인 항목 필터링
    leaderboard_df = leaderboard_manager.get_leaderboard()
    processing_df = leaderboard_df[leaderboard_df["status"] == "processing"]
    
    if not processing_df.empty:
        st.subheader("현재 진행 중인 퀴즈")
        
        for _, row in processing_df.iterrows():
            name = row["name"]
            api_endpoint = row["api_endpoint"]
            current_index = row["current_question_index"]
            total_questions = quiz_manager.get_total_questions()
            
            # 진행 상황 표시
            st.markdown(f"**{name}** ({api_endpoint})")
            progress = int(current_index) / total_questions if total_questions > 0 else 0
            st.progress(progress)
            st.text(f"문제 {current_index}/{total_questions} 진행 중")
            
            # 로그 표시
            logs = logger.get_user_log(name, api_endpoint)
            if logs:
                with st.expander("상세 로그 보기"):
                    for log in logs:
                        st.markdown(f"""
                        **문제 {log['question_index']}**: {log['question']}  
                        **응답**: {log['user_answer']}  
                        **정답**: {log['correct_answer']}  
                        **결과**: {'✅ 정답' if log['is_correct'] else '❌ 오답'}  
                        **응답 시간**: {log['response_time']:.2f}초
                        ---
                        """)
    else:
        st.info("현재 진행 중인 퀴즈가 없습니다.")
    
    # 오류 항목 표시
    error_df = leaderboard_df[leaderboard_df["status"] == "error"]
    if not error_df.empty:
        st.subheader("오류 발생 항목")
        st.dataframe(error_df[["name", "api_endpoint", "submission_time"]], use_container_width=True)

# Add footer
st.markdown("---")
st.markdown("AI Model Leaderboard - Powered by Streamlit and Hugging Face Spaces")

# 퀴즈 처리 함수
def process_quiz(name, api_endpoint):
    """
    사용자 API 엔드포인트로 퀴즈를 전송하고 결과를 처리합니다.
    """
    try:
        # API 클라이언트 초기화
        api_client = APIClient(api_endpoint)
        
        # 총 문제 수 가져오기
        total_questions = quiz_manager.get_total_questions()
        
        # 결과 저장 변수
        exact_match_results = []
        llm_judge_results = []
        response_times = []
        
        # 각 문제 처리
        for i in range(total_questions):
            # 현재 진행 상황 업데이트
            leaderboard_manager.update_question_progress(name, api_endpoint, i)
            
            # 문제 가져오기
            question_data = quiz_manager.get_question(i)
            correct_answer = quiz_manager.get_correct_answer(i)
            
            # API로 문제 전송
            response, response_time, success = api_client.send_question(question_data)
            
            if not success:
                logger.log_error(name, api_endpoint, f"API 호출 실패: 문제 {i}")
                leaderboard_manager.update_error_status(name, api_endpoint, f"API 호출 실패: 문제 {i}")
                return
            
            # 응답 검증
            if not api_client.validate_response(response):
                logger.log_error(name, api_endpoint, f"유효하지 않은 응답: 문제 {i}")
                leaderboard_manager.update_error_status(name, api_endpoint, f"유효하지 않은 응답: 문제 {i}")
                return
            
            # 사용자 답변 추출
            user_answer = response.get("answer", "")
            
            # Exact Match 채점
            is_correct = scorer.exact_match_score(user_answer, correct_answer)
            exact_match_results.append(is_correct)
            
            # LLM as Judge 채점
            llm_score, _ = scorer.llm_judge_score(user_answer, correct_answer, question_data.get("question_text", ""))
            llm_judge_results.append(llm_score)
            
            # 응답 시간 기록
            response_times.append(response_time)
            
            # 로그 기록
            logger.log_question_response(
                name, api_endpoint, i, 
                question_data.get("question_text", ""),
                user_answer, correct_answer,
                is_correct, response_time
            )
        
        # 최종 결과 계산
        correct_rate = scorer.calculate_total_score(exact_match_results) * 100
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        llm_result = sum(llm_judge_results) / len(llm_judge_results) if llm_judge_results else 0
        
        # 리더보드 업데이트
        leaderboard_manager.update_completion(
            name, api_endpoint, correct_rate, avg_response_time, str(llm_result)
        )
        
    except Exception as e:
        error_msg = f"처리 중 오류 발생: {str(e)}"
        logger.log_error(name, api_endpoint, error_msg)
        leaderboard_manager.update_error_status(name, api_endpoint, error_msg)