# 3kingdoms Quiz API 서버

이 API 서버는 3kingdoms Quiz 리더보드 시스템과 통신하기 위한 FastAPI 기반 서버입니다.

## API 명세

### 요청 (Request)

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

### 응답 (Response)

- **Content-Type**: application/json
- **Body**:
  ```json
  {
    "answer": "사용자의 답변 문자열"
  }
  ```

## 요구사항

1. **응답 시간**: 각 문제에 대한 응답은 최대 30초 이내에 반환되어야 합니다.
2. **안정성**: API는 연속적인 요청을 처리할 수 있어야 합니다.
3. **오류 처리**: API는 적절한 HTTP 상태 코드와 오류 메시지를 반환해야 합니다.

## 예제

### 요청 예시

```http
POST /answer
Content-Type: application/json

{
  "question": "( 연의 ) 손견의 아내인 오태부인은 임종 직전에 장소와 주유를 불러 말하기를, 손책을 낳을 때에는 ㅁ을 품는 꿈을 꾸었고, 손권을 낳을 때에는 해를 품는 꿈을 꾸었다고 말했다.",
  "question_id": "42",
  "difficulty": "hard"
}
```

### 응답 예시

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "answer": "달"
}
```

## 질문 유형과 답변 방식

삼국지 퀴즈는 다양한 유형의 질문이 포함될 수 있습니다:

1. **빈칸 채우기**: 주어진 문장에서 빈칸을 채우는 형태 (위 예제와 같음)
2. **인물 식별**: 특정 설명에 해당하는 인물의 이름을 답하는 형태
3. **사건 순서**: 사건의 순서나 결과를 묻는 형태
4. **장소 관련**: 특정 사건이 일어난 장소를 묻는 형태

답변은 가능한 한 간결하고 정확해야 합니다. 채점은 "exact match"와 "LLM as judge" 두 가지 방식으로 이루어지므로, 정확한 단어나 구문을 사용하는 것이 중요합니다.

## 서버 실행 방법

1. 필요한 패키지 설치:
   ```
   pip install -r requirements.txt
   ```

2. 서버 실행:
   ```
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

3. 서버가 실행되면 http://localhost:8000/answer 엔드포인트로 POST 요청을 보낼 수 있습니다.

## 커스터마이징

`main.py` 파일의 `get_answer` 함수를 수정하여 실제 질문에 대한 답변 로직을 구현하세요. 