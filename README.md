# 손 기능 재활 가상훈련 v3

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


## v3 수정 사항
- MediaPipe Tasks Vision CDN 경로를 `vision_bundle.mjs` 방식으로 수정했습니다.
- GPU delegate 로딩 실패 시 CPU delegate로 자동 전환합니다.
- 모델/카메라 로딩 오류가 화면에 표시되도록 보강했습니다.
- 우측 버튼이 눌리지 않고 `로딩 중`으로 고정되는 문제를 줄였습니다.


## v5 변경 사항

- 물방울 목표를 원형 아이콘이 아니라 실제 물방울에 가까운 물방울형 벡터 이미지로 표시합니다.
- 물컵을 투명 유리컵 형태로 표시하고, 물이 담긴 상태는 내부 물 높이와 수면으로 구분합니다.
- 물 따르기 과제의 주전자 이미지를 실제 물병 형태로 변경했습니다. 물병을 잡고 기울이는 단계에서는 물줄기가 함께 표시됩니다.
- 별도 이미지 파일 없이 HTML Canvas 벡터로 그리므로 Streamlit Cloud와 스마트폰 브라우저에서 추가 파일 의존성 없이 실행됩니다.
