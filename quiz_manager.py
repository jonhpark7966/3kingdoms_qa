import pandas as pd
from typing import Dict, List, Any, Optional

class QuizManager:
    """퀴즈 데이터를 로드하고 관리하는 클래스"""
    
    def __init__(self, quiz_data_path: str = "data/quiz_data.csv"):
        """
        퀴즈 관리자를 초기화합니다.
        
        Args:
            quiz_data_path: 퀴즈 데이터가 저장된 CSV 파일 경로
        """
        self.quiz_data_path = quiz_data_path
        self.quiz_data = None
        self.load_quiz_data()
    
    def load_quiz_data(self) -> None:
        """퀴즈 데이터를 CSV 파일에서 로드합니다."""
        try:
            self.quiz_data = pd.read_csv(self.quiz_data_path)
            # 필요한 컬럼이 있는지 확인
            required_columns = ['question', 'answer']
            if not all(col in self.quiz_data.columns for col in required_columns):
                raise ValueError(f"퀴즈 데이터에 필요한 컬럼이 없습니다: {required_columns}")
        except Exception as e:
            print(f"퀴즈 데이터 로드 중 오류 발생: {e}")
            # 기본 빈 DataFrame 생성
            self.quiz_data = pd.DataFrame(columns=['question', 'answer'])
    
    def get_question(self, index: int) -> Dict[str, Any]:
        """
        특정 인덱스의 퀴즈 문제를 API 요청 형식에 맞게 반환합니다.
        
        Args:
            index: 가져올 문제의 인덱스
            
        Returns:
            API 요청에 필요한 형식으로 포맷된 문제 데이터 딕셔너리
        """
        if self.quiz_data is None or index < 0 or index >= len(self.quiz_data):
            raise IndexError(f"유효하지 않은 문제 인덱스: {index}")
        
        # 해당 행을 딕셔너리로 변환
        question_data = self.quiz_data.iloc[index].to_dict()
        
        # API 요청 형식에 맞게 데이터 구성
        formatted_question = {
            "question": question_data.get('question', ''),
            "question_id": str(index),  # 인덱스를 question_id로 사용
            "difficulty": question_data.get('difficulty', 'medium')  # 기본 난이도 medium
        }
        
        return formatted_question
    
    def get_correct_answer(self, index: int) -> str:
        """
        특정 인덱스 문제의 정답을 반환합니다.
        
        Args:
            index: 정답을 가져올 문제의 인덱스
            
        Returns:
            문제의 정답 문자열
        """
        if self.quiz_data is None or index < 0 or index >= len(self.quiz_data):
            raise IndexError(f"유효하지 않은 문제 인덱스: {index}")
        
        # 'answer' 컬럼에서 정답 가져오기
        if 'answer' not in self.quiz_data.columns:
            raise ValueError("퀴즈 데이터에 'answer' 컬럼이 없습니다")
        
        return str(self.quiz_data.iloc[index]['answer'])
    
    def get_total_questions(self) -> int:
        """
        전체 퀴즈 문제 수를 반환합니다.
        
        Returns:
            전체 문제 수
        """
        if self.quiz_data is None:
            return 0
        return len(self.quiz_data)
    
    def get_all_questions(self) -> List[Dict[str, Any]]:
        """
        모든 퀴즈 문제를 API 요청 형식에 맞게 포맷하여 리스트로 반환합니다.
        
        Returns:
            API 요청 형식으로 포맷된 모든 문제 데이터의 딕셔너리 리스트
        """
        if self.quiz_data is None:
            return []
        
        formatted_questions = []
        for index, row in self.quiz_data.iterrows():
            question_data = row.to_dict()
            formatted_question = {
                "question": question_data.get('question', ''),
                "question_id": str(index),
                "difficulty": question_data.get('difficulty', 'medium')
            }
            formatted_question['question_text'] = question_data.get('question', '')
            formatted_questions.append(formatted_question)
        
        return formatted_questions
    
    def reload_quiz_data(self) -> None:
        """퀴즈 데이터를 다시 로드합니다."""
        self.load_quiz_data() 