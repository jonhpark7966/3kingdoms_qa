from typing import Dict, Any, List, Tuple, Optional
import logging

class Scorer:
    """퀴즈 응답을 채점하는 클래스"""
    
    def __init__(self):
        """채점 모듈을 초기화합니다."""
        self.logger = logging.getLogger(__name__)
    
    def exact_match_score(self, user_answer: str, correct_answer: str) -> bool:
        """
        정확한 일치 방식으로 응답을 채점합니다.
        
        Args:
            user_answer: 사용자 응답
            correct_answer: 정답
            
        Returns:
            정답이면 True, 오답이면 False
        """
        # 구현 필요
        pass
    
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
        # 구현 필요
        pass
    
    def calculate_total_score(self, results: List[bool]) -> float:
        """
        전체 정확도를 계산합니다.
        
        Args:
            results: 각 문제별 채점 결과 리스트
            
        Returns:
            정확도 (0.0 ~ 1.0)
        """
        # 구현 필요
        pass 