# 3kingdoms Quiz Leaderboard App 시스템 명세서

## 1. 개요


이 시스템은 사용자들이 자신의 이름과 FastAPI 엔드포인트를 제출하면, 준비된 퀴즈 데이터를 기반으로 API 호출을 통해 답변을 받고 채점 결과를 leaderboard.csv 파일에 기록하는 스트림릿 (Streamlit) 기반 리더보드 앱입니다.  

주요 특징은 다음과 같습니다:

- **사용자 입력**: 이름과 API 엔드포인트 제출
- **퀴즈 처리**: 준비된 CSV 기반 퀴즈를 API 호출하여 진행
- **채점 방식**: exact_match 방식과 LLM as judge 방식 (추후 관리자 재채점 포함)
- **실시간 모니터링**: 진행중인 퀴즈 상태와 질문/답변 로그 제공
- **오류 처리**: 오류 발생 시 해당 요청 중단 및 leaderboard에 상태 기록

## 2. 시스템 구성 요소

### 2.1. 스트림릿 (Streamlit) 앱

- **역할**:  
  - 사용자로부터 이름과 API 엔드포인트 입력을 받음  
  - leaderboard.csv 파일에 데이터를 기록 및 업데이트  
  - 현재 진행 중인 퀴즈 상태와 Q&A 로그를 실시간으로 모니터링 및 표시
   
- **주요 기능**:  
  - 입력 폼 제공 (이름, api_endpoint)
  - 제출 시 leaderboard.csv 파일 업데이트
  - 실시간 진행 상태(제출 시간, 완료 시간, 현재 문제 인덱스, 상태 등) 표시

### 2.2. FastAPI 엔드포인트

- **역할**:  
  - 사용자가 직접 구성하는 엔드포인트로, 시스템이 API 호출을 통해 퀴즈 질문을 전달하고 답변을 수신함  
   
- **요구 사항**:  
  - 적절한 응답 포맷 및 시간 내 응답
  - API 호출 오류 발생 시 적절한 에러 메시지 반환

### 2.3. 퀴즈 및 답변 데이터 관리

- **퀴즈 데이터**:  
  - CSV 파일(예: quiz_data.csv)로 준비되어 있으며, 각 문제와 정답 정보를 포함
 
- **리더보드 데이터**:  
  - CSV 파일(leaderboard.csv)로 관리
  - 주요 컬럼:
    - `name`: 사용자 이름
    - `api_endpoint`: 사용자가 제출한 API 엔드포인트
    - `correct_answer_rate`: 정확도(채점 결과)
    - `average_response_time`: 평균 응답 시간
    - `submission_time`: 제출 시간
    - `completion_time`: 채점 완료 시간
    - `current_question_index`: 전체 문제 중 현재 채점 진행중인 문제 인덱스
    - `status`: 진행 상태 (예: processing, completed, error 등)
    - `llm_judge_result`: LLM as judge 방식 채점 결과 (추후 관리자가 검토 및 재채점할 수 있도록 기록)

### 2.4. 채점 모듈
- **채점 방식**:
  - **Exact Match**: 단순 문자열 비교 방식으로 정답 여부를 판별
  - **LLM as Judge**: LLM을 활용한 채점 방식  
    - 해당 결과는 별도 컬럼(`llm_judge_result`)에 기록
    - 관리자 로그 확인 후 별도의 재채점 스크립트를 통해 검증 및 업데이트 진행 예정

## 3. 워크플로우

1. **사용자 제출**
   - 사용자가 스트림릿 앱에 접속하여 이름과 API 엔드포인트를 입력 후 제출.
   - 제출 시 `submission_time`과 함께 leaderboard.csv에 초기 레코드가 생성되고, `status`는 "processing"으로 설정.

2. **퀴즈 전송 및 응답 수신**
   - 시스템은 quiz_data.csv에서 준비된 문제를 선택하여 사용자의 API 엔드포인트로 전송.
   - 사용자의 엔드포인트가 응답을 반환하면, 응답 시간을 측정하고 로그에 기록.

3. **채점 처리**
   - **Exact Match** 방식으로 즉시 정답 여부 판별.
   - **LLM as Judge** 방식으로 채점 결과를 계산하여 별도의 컬럼에 기록 (추후 관리자 검토 대상).
   - 문제마다 채점 결과를 leaderboard에 업데이트하며, 현재 진행중인 문제의 인덱스(`current_question_index`)도 갱신.

4. **결과 업데이트 및 완료 처리**
   - 모든 문제의 채점이 완료되면 `completion_time` 기록.
   - 최종적으로 `correct_answer_rate`, `average_response_time` 등이 업데이트되어 리더보드에 반영됨.
   - 진행 상태(`status`)가 "completed"로 변경됨.

5. **오류 처리**
   - API 호출, 채점, 또는 CSV 업데이트 중 오류가 발생하면:
     - 해당 요청 처리 중단.
     - leaderboard.csv의 해당 레코드에 `status`를 "error"로 기록.
     - 사용자에게 오류 메시지 전달.

6. **실시간 모니터링 및 로그**
   - 진행 중인 질문/답변 상태 및 전체 Q&A 로그를 실시간으로 스트림릿 앱에서 모니터링할 수 있도록 표시.
   - 로그 파일 또는 별도의 CSV/데이터베이스로 저장하여 사용자들이 열람할 수 있게 함.

## 4. 데이터 모델 및 CSV 파일 구조

### 4.1. leaderboard.csv
| 컬럼 이름               | 데이터 타입  | 설명 |
|---------------------|-----------|-----|
| `name`              | 문자열      | 사용자 이름 |
| `api_endpoint`      | 문자열(URL) | 사용자 API 엔드포인트 |
| `correct_answer_rate` | 숫자/퍼센트  | 정확도 (채점 결과) |
| `average_response_time` | 숫자 (초)   | 평균 응답 시간 |
| `submission_time`   | 타임스탬프  | 제출 시각 |
| `completion_time`   | 타임스탬프  | 채점 완료 시각 |
| `current_question_index` | 정수      | 전체 문제 중 현재 진행중인 문제 번호 |
| `status`            | 문자열      | 처리 상태 (processing, completed, error 등) |
| `llm_judge_result`  | 문자열/숫자  | LLM as judge 방식 채점 결과 |

### 4.2. quiz_data.csv
- 각 행은 하나의 퀴즈 문제를 포함 (문제 텍스트, 정답, 기타 필요 정보)

## 5. 에러 및 예외 처리
- **API 호출 실패**:  
  - 타임아웃 또는 예외 발생 시 해당 요청 중단, `status`에 "error" 기록.
- **CSV 파일 업데이트 오류**:  
  - 파일 잠금 또는 쓰기 실패 발생 시 예외 처리 후 사용자에게 오류 메시지 전달.
- **채점 오류**:  
  - 채점 로직 중 발생한 문제는 해당 문제에 한해 `status`에 오류 기록 후 로그에 상세 기록.

## 6. 관리자 및 후속 처리
- **LLM as Judge 결과 검토**:
  - 관리자는 별도의 인터페이스 또는 스크립트를 통해 로그를 확인하고 LLM as judge 채점 결과를 재검토할 수 있음.
  - 재채점 스크립트는 csv 파일의 `llm_judge_result` 컬럼을 업데이트하도록 설계.

## 7. 파일 구조

```
3kingdoms-quiz-leaderboard/
│
├── app.py                     # 메인 Streamlit 앱 진입점
├── quiz_manager.py            # 퀴즈 데이터 관리 모듈
├── api_client.py              # API 호출 처리 모듈
├── scoring.py                 # 채점 로직 모듈
├── leaderboard_manager.py     # 리더보드 데이터 관리 모듈
├── logger.py                  # 로깅 모듈
├── utils.py                   # 유틸리티 함수 모듈
│
├── data/
│   ├── quiz_data.csv          # 퀴즈 문제 데이터
│   └── leaderboard.csv        # 리더보드 데이터
│
└── requirements.txt           # 필요한 패키지 목록
```

## 8. API 통신 명세

### 8.1. API 엔드포인트 요청 스펙

사용자는 다음 스펙을 준수하는 FastAPI 기반 엔드포인트를 구현해야 합니다:

#### 요청 (Request)

- **Method**: POST
- **Content-Type**: application/json
- **Body**:
  ```json
  {
    "question": "문제 텍스트",
    "question_id": "문제 고유 ID",
    "difficulty": "문제 난이도 (easy, medium, hard, very hard, super hard)"
  }
  ```

#### 응답 (Response)

- **Content-Type**: application/json
- **Body**:
  ```json
  {
    "answer": "사용자의 답변 문자열"
  }
  ```

#### 요구사항

1. **응답 시간**: 각 문제에 대한 응답은 최대 30초 이내에 반환되어야 합니다.
2. **안정성**: API는 연속적인 요청을 처리할 수 있어야 합니다.
3. **오류 처리**: API는 적절한 HTTP 상태 코드와 오류 메시지를 반환해야 합니다.

### 8.2. 예제

#### 요청 예시

```http
POST /your-endpoint
Content-Type: application/json

{
  "question": "( 연의 ) 손견의 아내인 오태부인은 임종 직전에 장소와 주유를 불러 말하기를, 손책을 낳을 때에는 ㅁ을 품는 꿈을 꾸었고, 손권을 낳을 때에는 해를 품는 꿈을 꾸었다고 말했다.",
  "question_id": "42",
  "difficulty": "hard"
}
```

#### 응답 예시

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "answer": "달"
}
```

### 8.3. 오류 처리

오류가 발생할 경우, 다음과 같은 HTTP 상태 코드와 함께 오류 메시지를 반환해야 합니다:

- **400 Bad Request**: 요청이 잘못된 경우
- **500 Internal Server Error**: 서버 내부 오류가 발생한 경우

예시:
```http
HTTP/1.1 400 Bad Request
Content-Type: application/json

{
  "error": "요청 형식이 올바르지 않습니다"
}
```

### 8.4. 채점 방식 안내

각 문제의 응답은 다음 두 가지 방식으로 채점됩니다:

1. **Exact Match**: 사용자의 답변(answer)과 정답이 정확히 일치하는지 여부
2. **LLM as Judge**: LLM을 활용해 사용자의 답변을 평가하는 방식

따라서, 사용자는 가능한 한 정확하고 간결한 답변을 제출하는 것이 유리합니다.
