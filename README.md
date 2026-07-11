# 손 기능 재활 가상훈련 Streamlit 앱 v2

이 앱은 뇌졸중 환자의 손 기능 재활을 위한 교육/피드백용 브라우저 기반 가상훈련 앱입니다. 스마트폰, 태블릿, PC 브라우저에서 실행되도록 **MediaPipe Hands Web(JavaScript)**를 사용합니다. 서버에는 Python MediaPipe, OpenCV, streamlit-webrtc가 필요하지 않습니다.

## 포함 훈련

- 물방울 잡아 터뜨리기: 손 쥐기
- 작은 물방울 집어 터뜨리기: 엄지-검지 집기
- 손 펴기 훈련: 물방울 위에서 손 펴기
- 가상 물컵 잡고 마시기
- 가상 물컵에 물 따르고 잡고 마시기

## 공통 난이도/과제 설정

모든 훈련 모드에서 다음 설정을 사용할 수 있습니다.

- 목표 물방울/과제 수
- 끝동작 유지 시간
- 손동작 인정 기준
- 물방울/물컵 크기 보정
- 물방울/물컵 속도 보정
- 훈련 손: 오른손 / 왼손 / 자동
- 손 떨림 보정/움직임 안정화
- 손 인식 최소 신뢰도

## 실행 방법

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

## 배포 방법

GitHub 저장소에 다음 파일을 업로드한 뒤 Streamlit Community Cloud에서 배포합니다.

```text
app.py
requirements.txt
packages.txt
.streamlit/config.toml
assets/audio/README.md
scripts/generate_korean_audio_edge_tts.py
README.md
```

`requirements.txt`는 다음처럼 단순합니다.

```text
streamlit>=1.38
```

`packages.txt`는 빈 파일입니다.

## 스마트폰/태블릿 음성 안내

모바일 브라우저에서는 Web Speech API 음성합성이 불안정할 수 있습니다. 가장 안정적인 방식은 `assets/audio/` 폴더에 한국어 안내 음성 mp3/wav 파일을 넣는 것입니다. 앱은 다음 순서로 안내를 출력합니다.

1. 녹음 음성 파일
2. 브라우저 음성합성
3. 신호음 + 진동 + 화면 안내

음성 파일 키 예시는 `assets/audio/README.md`를 확인하세요.

## 임상적 주의

이 앱은 교육용/피드백용 손 기능 재활 도구입니다. 단일 웹캠 기반 손 landmark 추정은 조명, 손 가림, 카메라 각도, 손 떨림, 마비 손의 변형에 영향을 받습니다. 임상 진단이나 치료 효과 판정에 사용하려면 별도 신뢰도·타당도 검증이 필요합니다.
