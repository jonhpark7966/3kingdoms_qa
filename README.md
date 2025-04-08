# 🏆 AI 모델 리더보드

다양한 AI 모델의 성능 지표를 추적하고 비교하는 Streamlit 웹 애플리케이션입니다.

## 📋 설명

이 애플리케이션은 다양한 AI 모델의 성능을 추적, 비교 및 시각화하는 간단한 방법을 제공합니다. API 엔드포인트와 주요 성능 지표를 포함하여 리더보드에 모델을 추가한 다음, 다양한 기준으로 정렬하고 비교할 수 있습니다.

## ✨ 주요 기능

- AI 모델의 정렬 가능한 리더보드 보기
- 성능 지표와 함께 새로운 AI 모델 추가
- 다음 기준으로 모델 정렬:
  - 정답률 (높은 순)
  - 응답 시간 (낮은 순)
  - 평균 토큰 수 (낮은 순)
  - 이름 (알파벳순)
- CSV 파일을 사용한 영구 저장소
- Streamlit을 활용한 깔끔하고 반응형 UI

## 🛠️ 설치 방법

1. 저장소 복제:
   ```bash
   git clone https://github.com/yourusername/ai-model-leaderboard.git
   cd ai-model-leaderboard
   ```

2. 필요한 의존성 설치:
   ```bash
   pip install -r requirements.txt
   ```

## 🚀 사용 방법

애플리케이션 실행:
```bash
streamlit run app.py
```