# 현재 개발 진행 상황과 남은 작업을 정리한 내용입니다.

### 모듈별 개발 상황

#### 기본 구조 및 설정
- ✅ 프로젝트 디렉토리 구조 설정
- ✅ Streamlit 앱 기본 구성 (app.py)
- ✅ 데이터 디렉토리 생성 로직 (data/)

#### 퀴즈 관리 모듈 (quiz_manager.py)
- ✅ QuizManager 클래스 구현
- ✅ 퀴즈 데이터 로드 및 관리 기능
- ✅ 문제 및 정답 조회 기능

#### 리더보드 관리 모듈 (leaderboard_manager.py)
- ✅ LeaderboardManager 클래스 구현
- ✅ 리더보드 CSV 파일 관리
- ✅ 제출 기록 추가 및 업데이트 기능
- ✅ 파일 잠금 기능을 통한 안전한 CSV 업데이트

#### API 클라이언트 모듈 (api_client.py)
- ✅ APIClient 클래스 기본 구조
- ❌ send_question 메서드 구현 필요
- ❌ validate_response 메서드 구현 필요

#### 채점 모듈 (scoring.py)
- ✅ Scorer 클래스 기본 구조
- ❌ exact_match_score 메서드 구현 필요
- ❌ llm_judge_score 메서드 구현 필요
- ❌ calculate_total_score 메서드 구현 필요

#### 로깅 모듈 (logger.py)
- ✅ QuizLogger 클래스 기본 구조
- ❌ setup_logging 메서드 구현 필요
- ❌ log_question_response 메서드 구현 필요
- ❌ log_error 메서드 구현 필요
- ❌ get_user_log 메서드 구현 필요

#### 유틸리티 모듈 (utils.py)
- ✅ 기본 함수 구조
- ❌ retry 데코레이터 구현 필요
- ❌ sanitize_input 함수 구현 필요
- ❌ format_time 함수 구현 필요
- ❌ safe_csv_update 함수 구현 필요

### Streamlit 앱 기능

- ✅ 리더보드 표시 탭
- ✅ API 제출 폼 구현
- ✅ 퀴즈 처리 워크플로우 구현
- ✅ 진행 상황 모니터링 탭
- ✅ 오류 항목 표시 기능

### 데이터 처리

- ✅ 리더보드 CSV 파일 관리
- ✅ 리더보드 정렬 및 필터링 기능
- ✅ 백그라운드 스레드를 통한 비동기 퀴즈 처리
- ❌ 채점 결과 정확한 계산 (구현 필요한 함수에 의존)

### 우선 구현 필요 항목

1. API 클라이언트의 실제 요청 및 응답 처리
   - API 엔드포인트 호출 기능
   - 응답 검증 및 오류 처리

2. 채점 모듈의 정확한 채점 로직
   - Exact Match 방식 구현
   - LLM as Judge 방식 구현
   - 채점 결과 계산 로직

3. 로깅 모듈의 세부 구현
   - 로그 파일 관리
   - 세부 로깅 기능
   - 사용자별 로그 조회

4. 유틸리티 함수 구현
   - 안전한 CSV 업데이트 기능
   - 입력 검증 및 정제 함수
   - 재시도 로직
