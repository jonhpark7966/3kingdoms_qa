import logging
import os
import json
from datetime import datetime
from typing import Dict, Any, List, Optional

class QuizLogger:
    """퀴즈 수행 로그를 관리하는 클래스"""
    
    def __init__(self, log_dir: str = "logs"):
        """
        로거를 초기화합니다.
        
        Args:
            log_dir: 로그 파일이 저장될 디렉토리
        """
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        self.setup_logging()
    
    def setup_logging(self) -> None:
        """로깅 설정을 구성합니다."""
        # 공통 로깅 설정
        self.logger = logging.getLogger("quiz_app")
        self.logger.setLevel(logging.INFO)
        
        # 로그 포맷 설정
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        # 콘솔 핸들러 추가
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # 파일 핸들러 추가
        file_handler = logging.FileHandler(os.path.join(self.log_dir, "quiz_app.log"))
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        
        # 사용자 상호작용 로그를 저장할 JSON 파일 경로
        self.interaction_log_path = os.path.join(self.log_dir, "interactions.json")
        
        # 상호작용 로그 파일이 없으면 빈 리스트로 초기화
        if not os.path.exists(self.interaction_log_path):
            with open(self.interaction_log_path, "w", encoding="utf-8") as f:
                json.dump([], f)
    
    def log_question_response(self, name: str, api_endpoint: str, 
                             question_index: int, question: str, 
                             user_answer: str, correct_answer: str,
                             is_correct: bool, llm_score: float, response_time: float) -> None:
        """
        질문과 응답을 로그에 기록합니다.
        
        Args:
            name: 사용자 이름
            api_endpoint: API 엔드포인트
            question_index: 문제 인덱스
            question: 문제 텍스트
            user_answer: 사용자 응답
            correct_answer: 정답
            is_correct: 정답 여부
            response_time: 응답 시간
        """
        # 로깅 메시지 생성
        log_message = (
            f"User: {name}, API: {api_endpoint}, Question #{question_index}, "
            f"Answer: '{user_answer}', Correct: {is_correct}, LLM Score: {llm_score:.2f}, Time: {response_time:.2f}s"
        )
        self.logger.info(log_message)
        
        # 상세 로그를 JSON 형식으로 저장
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "question_response",
            "name": name,
            "api_endpoint": api_endpoint,
            "question_index": question_index,
            "question": question,
            "user_answer": user_answer,
            "correct_answer": correct_answer,
            "is_correct": is_correct,
            "llm_score": llm_score,
            "response_time": response_time
        }
        
        # 로그 파일에 추가
        self._append_to_log_file(log_entry)
    
    def log_error(self, name: str, api_endpoint: str, error_msg: str) -> None:
        """
        오류를 로그에 기록합니다.
        
        Args:
            name: 사용자 이름
            api_endpoint: API 엔드포인트
            error_msg: 오류 메시지
        """
        # 로깅 메시지 생성
        log_message = f"ERROR - User: {name}, API: {api_endpoint}, Error: {error_msg}"
        self.logger.error(log_message)
        
        # 상세 로그를 JSON 형식으로 저장
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "error",
            "name": name,
            "api_endpoint": api_endpoint,
            "error_message": error_msg
        }
        
        # 로그 파일에 추가
        self._append_to_log_file(log_entry)
    
    def get_user_log(self, name: str, api_endpoint: str) -> List[Dict[str, Any]]:
        """
        특정 사용자의 로그를 가져옵니다.
        
        Args:
            name: 사용자 이름
            api_endpoint: API 엔드포인트
            
        Returns:
            사용자 로그 항목 리스트
        """
        # 로그 파일에서 모든 로그 항목 읽기
        all_logs = self._read_log_file()
        
        # 특정 사용자의 로그만 필터링
        user_logs = [
            log for log in all_logs
            if log.get("name") == name and log.get("api_endpoint") == api_endpoint
        ]
        
        return user_logs
    
    def _append_to_log_file(self, log_entry: Dict[str, Any]) -> None:
        """
        로그 항목을 로그 파일에 추가합니다.
        
        Args:
            log_entry: 추가할 로그 항목
        """
        all_logs = self._read_log_file()
        all_logs.append(log_entry)
        
        with open(self.interaction_log_path, "w", encoding="utf-8") as f:
            json.dump(all_logs, f, ensure_ascii=False, indent=2)
    
    def _read_log_file(self) -> List[Dict[str, Any]]:
        """
        로그 파일에서 모든 로그 항목을 읽습니다.
        
        Returns:
            모든 로그 항목 리스트
        """
        try:
            with open(self.interaction_log_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return [] 