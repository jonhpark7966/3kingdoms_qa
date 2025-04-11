from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
import os
from openai import OpenAI


app = FastAPI(title="3kingdoms Quiz API")

# OpenAI 클라이언트 초기화
client = OpenAI(api_key="")

class QuizQuestion(BaseModel):
    question: str
    question_id: str
    difficulty: str

class QuizAnswer(BaseModel):
    answer: str

@app.post("/answer", response_model=QuizAnswer)
async def answer_question(question: QuizQuestion):
    """
    API 엔드포인트: 퀴즈 질문을 받아 답변을 반환합니다.
    
    GPT-4o-mini 모델을 사용하여 답변을 생성합니다.
    """
    try:
        print(f"[요청 받음] 질문 ID: {question.question_id}, 난이도: {question.difficulty}")
        print(f"[질문 내용] {question.question}")
        
        answer = get_answer(question.question, question.question_id, question.difficulty)
        
        print(f"[응답 생성] 질문 ID: {question.question_id}, 답변: {answer}")
        return QuizAnswer(answer=answer)
    except Exception as e:
        print(f"[오류 발생] 질문 ID: {question.question_id}, 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")

def get_answer(question: str, question_id: str, difficulty: str) -> str:
    """
    질문에 대한 답변을 생성하는 함수
    
    GPT-4o-mini 모델을 사용하여 삼국지 퀴즈 질문에 대한 답변을 생성합니다.
    
    Args:
        question: 질문 텍스트
        question_id: 질문 고유 ID
        difficulty: 질문 난이도
        
    Returns:
        str: 질문에 대한 답변
    """
    try:
        # OpenAI API 호출
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # GPT-4o-mini 모델 사용
            messages=[
                {"role": "system", "content": "당신은 삼국지에 대한 전문가입니다. 삼국지 관련 퀴즈 질문에 정확하고 간결하게 단답형으로 답변해 주세요."},
                {"role": "user", "content": f"질문: ( 연의 ) 유비가 서천을 평정하자, 손권은 형주를 돌려받기 위해, _____의 가족을 거짓으로 인질로 잡고는 그를 유비에게 사신으로 보내어 형주를 돌려달라고 했다."},
                {"role": "assistant", "content": f"제갈근"},
                {"role": "user", "content": f"질문: ( 연의 ) 손권은 관우를 죽이고 나서 연회를 열어 장수들의 전공을 축하했는데, 이 자리에서 '조조를 적벽에서 이긴 주유나 ㅁ주 지배를 하지 못한 노숙보다 여몽이 더 뛰어나다' 고 여몽에게 말했다."},
                {"role": "assistant", "content": f"형"},
                {"role": "user", "content": f"질문: {question}"}
            ],
            max_tokens=300,
            temperature=0.3,  # 정확한 답변을 위해 낮은 temperature 설정
        )
        
        # API 응답에서 답변 추출
        answer = response.choices[0].message.content.strip()
        return answer
    
    except Exception as e:
        # 오류 발생 시 로그 기록 후 기본 메시지 반환
        print(f"OpenAI API 호출 오류: {str(e)}")
        return f"죄송합니다. 답변을 생성하는 중 오류가 발생했습니다. (오류 코드: {question_id})"

@app.get("/")
async def root():
    """루트 엔드포인트: API 상태 확인용"""
    return {"status": "online", "message": "3kingdoms Quiz API 서버가 실행 중입니다"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 