from typing import Dict, Any, List, Tuple, Optional
import logging
from openai import OpenAI

class Scorer:
    """퀴즈 응답을 채점하는 클래스"""
    
    def __init__(self):
        """채점 모듈을 초기화합니다."""
        self.logger = logging.getLogger(__name__)
        # OpenAI API 설정
        self.openai_api_key = ""
        self.openai_api_base = "http://192.168.233.143:8000/v1"
        self.client = OpenAI(
            api_key=self.openai_api_key,
            #base_url=self.openai_api_base,
        )
    
    def exact_match_score(self, user_answer: str, correct_answer: str) -> bool:
        """
        정확한 일치 방식으로 응답을 채점합니다.
        
        Args:
            user_answer: 사용자 응답
            correct_answer: 정답
            
        Returns:
            정답이면 True, 오답이면 False
        """
        if user_answer is None or correct_answer is None:
            return False
            
        # 양쪽 공백 제거 및 소문자 변환으로 전처리
        user_answer = user_answer.strip().lower()
        correct_answer = correct_answer.strip().lower()
        
        # 정확히 일치하는지 확인
        return user_answer == correct_answer
    
    def llm_judge_score(self, user_answer: str, correct_answer: str, question: str) -> Tuple[float, str]:
        """
        LLM as judge 방식으로 응답을 채점합니다.
        
        Args:
            user_answer: 사용자 응답
            correct_answer: 정답
            question: 문제 텍스트
            
        Returns:
            (점수, 채점 근거) 튜플
        """
        prompt = f"""Score the student answer as either CORRECT or INCORRECT.

Example Format:
QUESTION: question here
STUDENT ANSWER: student's answer here
TRUE ANSWER: true answer here
GRADE: CORRECT or INCORRECT here

Grade the student answers based ONLY on their factual accuracy. Ignore differences in punctuation and phrasing between the student answer and true answer.
It is OK if the student answer contains more information than the true answer, as long as it does not contain any conflicting statements. Begin! 

QUESTION: {question}
STUDENT ANSWER: {user_answer}
TRUE ANSWER: {correct_answer}
GRADE:"""

        try:
            chat_response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a Teacher to grade your student's answer."},
                    {"role": "user", "content": prompt},
                ]
            )
            
            judgement = chat_response.choices[0].message.content.strip()
            is_correct = False if "INCORRECT" in judgement else True
            
            # 점수 (1.0 = 정답, 0.0 = 오답)과 채점 근거 반환
            score = 1.0 if is_correct else 0.0
            
            return score, judgement
        except Exception as e:
            self.logger.error(f"LLM 판단 중 오류 발생: {str(e)}")
            # 오류 발생 시 기본적으로 오답 처리 및 오류 메시지 반환
            return 0.0, f"Error during LLM judge: {str(e)}"
    
    def calculate_total_score(self, results: List[bool]) -> float:
        """
        전체 정확도를 계산합니다.
        
        Args:
            results: 각 문제별 채점 결과 리스트
            
        Returns:
            정확도 (0.0 ~ 1.0)
        """
        if not results:
            return 0.0
            
        # 정답 수 / 전체 문제 수
        correct_count = sum(1 for result in results if result)
        return correct_count / len(results) 