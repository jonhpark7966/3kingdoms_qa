import requests
import time
from typing import Dict, Any, Tuple, Optional
import logging

class APIClient:
    """사용자 API 엔드포인트와 통신하는 클래스"""
    
    def __init__(self, api_endpoint: str, timeout: int = 30):
        """
        API 클라이언트를 초기화합니다.
        
        Args:
            api_endpoint: 사용자가 제출한 API 엔드포인트 URL
            timeout: API 요청 타임아웃 시간(초)
        """
        self.api_endpoint = api_endpoint
        self.timeout = timeout
        self.logger = logging.getLogger(__name__)
    
    def send_question(self, question_data: Dict[str, Any]) -> Tuple[Optional[Dict[str, Any]], float, bool]:
        """
        문제를 API 엔드포인트로 전송하고 응답을 받습니다.
        
        Args:
            question_data: API로 전송할 문제 데이터
            
        Returns:
            (응답 데이터, 응답 시간(초), 성공 여부) 튜플
        """
        start_time = time.time()
        success = False
        response_data = None
        
        try:
            # API 엔드포인트로 POST 요청 전송
            response = requests.post(
                self.api_endpoint,
                json=question_data,
                timeout=self.timeout
            )
            
            # HTTP 응답 상태 코드 확인
            if response.status_code == 200:
                response_data = response.json()
                success = self.validate_response(response_data)
            else:
                self.logger.error(f"API 요청 실패: 상태 코드 {response.status_code}")
                self.logger.error(f"응답 내용: {response.text}")
                
        except requests.exceptions.Timeout:
            self.logger.error(f"API 요청 타임아웃: {self.timeout}초 초과")
        except requests.exceptions.ConnectionError:
            self.logger.error(f"API 연결 오류: {self.api_endpoint}에 연결할 수 없음")
        except requests.exceptions.RequestException as e:
            self.logger.error(f"API 요청 오류: {str(e)}")
        except Exception as e:
            self.logger.error(f"예상치 못한 오류: {str(e)}")
            
        elapsed_time = time.time() - start_time
        return response_data, elapsed_time, success
    
    def validate_response(self, response: Dict[str, Any]) -> bool:
        """
        API 응답의 유효성을 검증합니다.
        
        Args:
            response: API 응답 데이터
            
        Returns:
            응답이 유효하면 True, 그렇지 않으면 False
        """
        # 응답에 'answer' 필드가 있고, 문자열인지 확인
        if 'answer' not in response:
            self.logger.error("API 응답에 'answer' 필드가 없습니다")
            return False
            
        if not isinstance(response['answer'], str):
            self.logger.error("API 응답의 'answer' 필드가 문자열이 아닙니다")
            return False
            
        return True 