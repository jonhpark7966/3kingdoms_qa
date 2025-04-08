import pandas as pd
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
import time
import csv
import fcntl

class LeaderboardManager:
    """리더보드 데이터를 관리하는 클래스"""
    
    def __init__(self, leaderboard_path: str = "data/leaderboard.csv"):
        """
        리더보드 관리자를 초기화합니다.
        
        Args:
            leaderboard_path: 리더보드 CSV 파일 경로
        """
        self.leaderboard_path = leaderboard_path
        self.logger = logging.getLogger(__name__)
        self._ensure_leaderboard_exists()
    
    def _ensure_leaderboard_exists(self) -> None:
        """리더보드 CSV 파일이 없으면 생성합니다."""
        os.makedirs(os.path.dirname(self.leaderboard_path), exist_ok=True)
        
        if not os.path.exists(self.leaderboard_path):
            # 명세서에 정의된 컬럼으로 빈 CSV 파일 생성
            columns = [
                "name", "api_endpoint", "correct_answer_rate", 
                "average_response_time", "submission_time", 
                "completion_time", "current_question_index", 
                "status", "llm_judge_result"
            ]
            
            df = pd.DataFrame(columns=columns)
            df.to_csv(self.leaderboard_path, index=False)
            self.logger.info(f"새 리더보드 파일 생성: {self.leaderboard_path}")
    
    def _acquire_lock(self, file_obj):
        """파일에 락을 설정합니다."""
        try:
            fcntl.flock(file_obj, fcntl.LOCK_EX | fcntl.LOCK_NB)
            return True
        except (IOError, OSError):
            self.logger.warning("파일 락 획득 실패, 재시도 중...")
            time.sleep(0.1)
            return False
    
    def _release_lock(self, file_obj):
        """파일 락을 해제합니다."""
        try:
            fcntl.flock(file_obj, fcntl.LOCK_UN)
        except (IOError, OSError) as e:
            self.logger.error(f"파일 락 해제 실패: {e}")
    
    def _safe_update_csv(self, update_func) -> bool:
        """
        CSV 파일을 안전하게 업데이트합니다.
        
        Args:
            update_func: 데이터프레임을 업데이트하는 함수
            
        Returns:
            업데이트 성공 여부
        """
        max_retries = 5
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                # 파일이 없으면 생성
                self._ensure_leaderboard_exists()
                
                # 파일 열기
                with open(self.leaderboard_path, 'r+') as f:
                    # 락 획득 시도
                    if not self._acquire_lock(f):
                        retry_count += 1
                        continue
                    
                    try:
                        # 현재 데이터 읽기
                        df = pd.read_csv(self.leaderboard_path)
                        
                        # 업데이트 함수 실행
                        updated_df = update_func(df)
                        
                        # 파일 처음으로 되돌리고 내용 지우기
                        f.seek(0)
                        f.truncate()
                        
                        # 업데이트된 데이터 쓰기
                        updated_df.to_csv(f, index=False)
                        
                        return True
                    finally:
                        # 락 해제
                        self._release_lock(f)
            
            except (IOError, OSError, pd.errors.EmptyDataError) as e:
                self.logger.error(f"CSV 업데이트 중 오류 발생: {e}")
                retry_count += 1
                time.sleep(0.2)  # 재시도 전 잠시 대기
        
        self.logger.error(f"최대 재시도 횟수({max_retries})를 초과했습니다.")
        return False
    
    def add_new_submission(self, name: str, api_endpoint: str) -> bool:
        """
        새 제출 기록을 리더보드에 추가합니다.
        
        Args:
            name: 사용자 이름
            api_endpoint: API 엔드포인트
            
        Returns:
            성공 여부
        """
        def update_func(df):
            # 이미 존재하는지 확인
            existing = df[(df['name'] == name) & (df['api_endpoint'] == api_endpoint)]
            
            if not existing.empty:
                # 이미 처리 중이거나 완료된 항목이 있으면 새 항목 추가하지 않음
                self.logger.warning(f"이미 존재하는 제출: {name}, {api_endpoint}")
                return df
            
            # 현재 시간
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # 새 항목 생성
            new_row = {
                'name': name,
                'api_endpoint': api_endpoint,
                'correct_answer_rate': 0.0,
                'average_response_time': 0.0,
                'submission_time': now,
                'completion_time': None,
                'current_question_index': 0,
                'status': 'processing',
                'llm_judge_result': None
            }
            
            # 데이터프레임에 추가
            return pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        
        return self._safe_update_csv(update_func)
    
    def update_question_progress(self, name: str, api_endpoint: str, 
                                current_index: int) -> bool:
        """
        현재 진행 중인 문제 인덱스를 업데이트합니다.
        
        Args:
            name: 사용자 이름
            api_endpoint: API 엔드포인트
            current_index: 현재 진행 중인 문제 인덱스
            
        Returns:
            업데이트 성공 여부
        """
        def update_func(df):
            # 해당 항목 찾기
            mask = (df['name'] == name) & (df['api_endpoint'] == api_endpoint)
            
            if mask.any():
                df.loc[mask, 'current_question_index'] = current_index
            else:
                self.logger.warning(f"업데이트할 항목을 찾을 수 없음: {name}, {api_endpoint}")
            
            return df
        
        return self._safe_update_csv(update_func)
    
    def update_completion(self, name: str, api_endpoint: str, 
                         correct_rate: float, avg_response_time: float,
                         llm_result: str) -> bool:
        """
        채점 완료 후 결과를 업데이트합니다.
        
        Args:
            name: 사용자 이름
            api_endpoint: API 엔드포인트
            correct_rate: 정확도
            avg_response_time: 평균 응답 시간
            llm_result: LLM as judge 결과
            
        Returns:
            업데이트 성공 여부
        """
        def update_func(df):
            # 해당 항목 찾기
            mask = (df['name'] == name) & (df['api_endpoint'] == api_endpoint)
            
            if mask.any():
                # 현재 시간
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # 결과 업데이트
                df.loc[mask, 'correct_answer_rate'] = correct_rate
                df.loc[mask, 'average_response_time'] = avg_response_time
                df.loc[mask, 'completion_time'] = now
                df.loc[mask, 'status'] = 'completed'
                df.loc[mask, 'llm_judge_result'] = llm_result
            else:
                self.logger.warning(f"업데이트할 항목을 찾을 수 없음: {name}, {api_endpoint}")
            
            return df
        
        return self._safe_update_csv(update_func)
    
    def update_error_status(self, name: str, api_endpoint: str, error_msg: str) -> bool:
        """
        오류 상태를 업데이트합니다.
        
        Args:
            name: 사용자 이름
            api_endpoint: API 엔드포인트
            error_msg: 오류 메시지
            
        Returns:
            업데이트 성공 여부
        """
        def update_func(df):
            # 해당 항목 찾기
            mask = (df['name'] == name) & (df['api_endpoint'] == api_endpoint)
            
            if mask.any():
                # 현재 시간
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # 오류 상태 업데이트
                df.loc[mask, 'status'] = 'error'
                df.loc[mask, 'completion_time'] = now
                
                # 오류 메시지는 로그에만 기록하고 CSV에는 저장하지 않음
                self.logger.error(f"오류 발생 ({name}, {api_endpoint}): {error_msg}")
            else:
                self.logger.warning(f"업데이트할 항목을 찾을 수 없음: {name}, {api_endpoint}")
            
            return df
        
        return self._safe_update_csv(update_func)
    
    def get_leaderboard(self) -> pd.DataFrame:
        """
        현재 리더보드 데이터를 반환합니다.
        
        Returns:
            리더보드 데이터프레임
        """
        try:
            # 파일이 없으면 생성
            self._ensure_leaderboard_exists()
            
            # 데이터 읽기
            df = pd.read_csv(self.leaderboard_path)
            return df
        except Exception as e:
            self.logger.error(f"리더보드 데이터 로드 중 오류 발생: {e}")
            # 오류 발생 시 빈 데이터프레임 반환
            columns = [
                "name", "api_endpoint", "correct_answer_rate", 
                "average_response_time", "submission_time", 
                "completion_time", "current_question_index", 
                "status", "llm_judge_result"
            ]
            return pd.DataFrame(columns=columns) 