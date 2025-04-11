import time
from typing import Dict, Any, Callable, Optional, TypeVar, List
import pandas as pd
import logging

T = TypeVar('T')

def retry(func: Callable[..., T], max_retries: int = 3, 
          retry_delay: float = 1.0) -> Callable[..., Optional[T]]:
    """
    함수 실행을 재시도하는 데코레이터를 반환합니다.
    
    Args:
        func: 재시도할 함수
        max_retries: 최대 재시도 횟수
        retry_delay: 재시도 간 대기 시간(초)
        
    Returns:
        재시도 로직이 포함된 래퍼 함수
    """
    def wrapper(*args, **kwargs):
        attempts = 0
        last_exception = None
        
        while attempts < max_retries:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                attempts += 1
                last_exception = e
                logging.warning(f"Attempt {attempts}/{max_retries} failed for {func.__name__}: {str(e)}")
                if attempts < max_retries:
                    time.sleep(retry_delay)
        
        logging.error(f"All {max_retries} attempts failed for {func.__name__}: {str(last_exception)}")
        return None
        
    return wrapper

def sanitize_input(text: str) -> str:
    """
    입력 텍스트를 안전하게 정제합니다.
    
    Args:
        text: 정제할 텍스트
        
    Returns:
        정제된 텍스트
    """
    if text is None:
        return ""
    
    # 앞뒤 공백 제거
    text = text.strip()
    
    # HTML 태그 및 특수 문자 이스케이프 처리
    text = text.replace("<", "&lt;").replace(">", "&gt;")
    
    # 줄바꿈 문자 정규화
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    
    return text

def format_time(seconds: float) -> str:
    """
    초 단위 시간을 읽기 쉬운 형식으로 포맷합니다.
    
    Args:
        seconds: 시간(초)
        
    Returns:
        포맷된 시간 문자열
    """
    if seconds < 0:
        return "0초"
    
    if seconds < 1:
        # 1초 미만은 밀리초로 표시
        return f"{seconds*1000:.0f}ms"
    
    if seconds < 60:
        # 1분 미만은 초로 표시
        return f"{seconds:.1f}초"
    
    minutes, seconds = divmod(seconds, 60)
    if minutes < 60:
        # 1시간 미만은 분:초로 표시
        return f"{int(minutes)}분 {int(seconds)}초"
    
    hours, minutes = divmod(minutes, 60)
    # 1시간 이상은 시:분:초로 표시
    return f"{int(hours)}시간 {int(minutes)}분 {int(seconds)}초"

def safe_csv_update(df: pd.DataFrame, csv_path: str) -> bool:
    """
    CSV 파일을 안전하게 업데이트합니다.
    
    Args:
        df: 저장할 데이터프레임
        csv_path: CSV 파일 경로
        
    Returns:
        성공 여부
    """
    try:
        # 임시 파일 경로 생성
        temp_path = f"{csv_path}.tmp"
        
        # 임시 파일에 먼저 저장
        df.to_csv(temp_path, index=False, encoding='utf-8')
        
        # 파일 시스템 동기화 (플러시)
        import os
        os.fsync(open(temp_path, 'r+').fileno())
        
        # 기존 파일 백업 (기존 파일이 있는 경우)
        backup_path = f"{csv_path}.bak"
        if os.path.exists(csv_path):
            if os.path.exists(backup_path):
                os.remove(backup_path)
            os.rename(csv_path, backup_path)
        
        # 임시 파일을 정식 파일로 이름 변경
        os.rename(temp_path, csv_path)
        
        # 성공적으로 업데이트됨
        logging.info(f"Successfully updated {csv_path}")
        return True
        
    except Exception as e:
        logging.error(f"Error updating {csv_path}: {str(e)}")
        return False 