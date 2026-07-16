from __future__ import annotations

import base64
import json
import mimetypes
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

APP_DIR = Path(__file__).parent
AUDIO_DIR = APP_DIR / "assets" / "audio"

st.set_page_config(
    page_title="손 기능 재활 가상훈련",
    page_icon="🖐️",
    layout="wide",
    initial_sidebar_state="expanded",
)


def load_audio_assets() -> dict[str, dict[str, str]]:
    """Load optional pre-recorded Korean audio files as base64 data URIs.

    Mobile browsers often block Web Speech API output inside embedded apps.
    If MP3/WAV files with matching keys are placed in assets/audio/, the browser
    plays those files first and falls back to speech synthesis, tones, and vibration.
    """
    assets: dict[str, dict[str, str]] = {}
    if not AUDIO_DIR.exists():
        return assets
    for path in AUDIO_DIR.iterdir():
        if not path.is_file() or path.suffix.lower() not in {".mp3", ".wav", ".ogg", ".m4a"}:
            continue
        mime = mimetypes.guess_type(path.name)[0] or "audio/mpeg"
        data = base64.b64encode(path.read_bytes()).decode("ascii")
        assets[path.stem] = {"mime": mime, "data": f"data:{mime};base64,{data}"}
    return assets

IMAGE_DIR = APP_DIR / "assets" / "images"

def load_image_assets() -> dict[str, str]:
    """Load high-quality PNG sprites for more photo-like canvas graphics."""
    assets: dict[str, str] = {}
    if not IMAGE_DIR.exists():
        return assets
    for path in IMAGE_DIR.iterdir():
        if not path.is_file() or path.suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp"}:
            continue
        mime = mimetypes.guess_type(path.name)[0] or "image/png"
        data = base64.b64encode(path.read_bytes()).decode("ascii")
        assets[path.stem] = f"data:{mime};base64,{data}"
    return assets


EXERCISES = {
    "bubble_pinch": {
        "label": "작은 물방울 집어 터뜨리기: 엄지-검지 집기",
        "taskType": "bubble",
        "gesture": "pinch",
        "targetName": "작은 물방울",
        "description": "검지 끝을 물방울에 가져간 뒤 엄지와 검지를 맞대면 성공합니다.",
        "clinicalGoal": "pinch, 세밀한 손 조절, 손-눈 협응",
    },
    "open_hand": {
        "label": "손 펴기 훈련: 물방울 위에서 손 펴기",
        "taskType": "bubble",
        "gesture": "open",
        "targetName": "물방울",
        "description": "손바닥 중심을 물방울에 가져간 뒤 손을 충분히 펴면 성공합니다.",
        "clinicalGoal": "손가락 신전, 주먹 쥔 자세에서 손 펴기 피드백",
    },
    "cup_grasp_drink": {
        "label": "가상 물컵 잡고 마시기",
        "taskType": "cup_drink",
        "gesture": "grasp",
        "targetName": "물컵",
        "description": "가상 물컵을 손으로 잡은 뒤 입 위치 목표까지 옮겨 잠시 멈추면 성공합니다.",
        "clinicalGoal": "컵 잡기, 운반, 입으로 가져가기, 일상생활동작 과제 지향 훈련",
    },
    "air_bubble_grasp": {
        "label": "손 주변 공기방울 잡아 터뜨리기",
        "taskType": "hand_bubbles",
        "gesture": "grasp",
        "targetName": "공기방울",
        "description": "손 주변에 나타나는 여러 공기방울 중 하나로 손을 이동한 뒤 손을 쥐어 터뜨리면 성공합니다.",
        "clinicalGoal": "상지 도달, 손-눈 협응, 손가락 굴곡, 선택적 grasp 반응, 반복적 과제 지향 훈련",
    },
}

LEVELS = {
    1: {
        "name": "1단계: 중증/초기 - 매우 쉬움",
        "targetRadius": 105,
        "speed": 0.0,
        "holdMs": 250,
        "gestureThreshold": 0.15,
        "targetCount": 5,
        "tiltDeg": 12,
        "description": "큰 고정 목표, 손동작 요구 최소화, 접촉 중심",
    },
    2: {
        "name": "2단계: 중등도 - 큰 목표 + 낮은 손동작 기준",
        "targetRadius": 90,
        "speed": 0.2,
        "holdMs": 400,
        "gestureThreshold": 0.30,
        "targetCount": 7,
        "tiltDeg": 16,
        "description": "큰 목표와 느린 이동, 약한 손 쥐기/펴기/집기 허용",
    },
    3: {
        "name": "3단계: 표준 - 목표 위치와 끝동작 유지",
        "targetRadius": 74,
        "speed": 0.45,
        "holdMs": 650,
        "gestureThreshold": 0.45,
        "targetCount": 10,
        "tiltDeg": 22,
        "description": "표준 크기 목표, 끝동작을 일정 시간 유지해야 성공",
    },
    4: {
        "name": "4단계: 경도 - 작은 이동 목표",
        "targetRadius": 60,
        "speed": 0.8,
        "holdMs": 850,
        "gestureThreshold": 0.60,
        "targetCount": 12,
        "tiltDeg": 28,
        "description": "작은 목표, 이동 목표, 더 명확한 손 기능 조절 요구",
    },
    5: {
        "name": "5단계: 도전 - 작은 목표 + 빠른 이동 + 정확도 요구",
        "targetRadius": 50,
        "speed": 1.15,
        "holdMs": 1050,
        "gestureThreshold": 0.72,
        "targetCount": 15,
        "tiltDeg": 34,
        "description": "빠르고 작은 목표, 높은 정확도와 더 긴 끝동작 유지 요구",
    },
}

st.title("🖐️ 뇌졸중 환자 손 기능 재활 가상훈련 v31")
st.caption("MediaPipe Hands Web 기반 · 스마트폰/태블릿 브라우저 실행 · Python MediaPipe/OpenCV 불필요")

with st.expander("📱 훈련 설정: 스마트폰에서도 여기에서 조정", expanded=True):
    st.header("훈련 설정")
    exercise_key = st.selectbox(
        "훈련 과제",
        options=list(EXERCISES.keys()),
        format_func=lambda k: EXERCISES[k]["label"],
        index=3,
    )
    affected_hand = st.radio(
        "훈련 손",
        options=["Right", "Left", "Any"],
        format_func=lambda v: {"Right": "오른손", "Left": "왼손", "Any": "자동/보이는 손"}[v],
        horizontal=True,
    )
    level = st.slider("난이도", min_value=1, max_value=5, value=2, step=1)
    level_cfg = LEVELS[level]
    target_count = st.slider("목표 물방울/공기방울/반복 수", min_value=3, max_value=30, value=level_cfg["targetCount"], step=1)
    hold_ms = st.slider("끝동작 유지 시간(ms)", min_value=200, max_value=2500, value=level_cfg["holdMs"], step=50)
    step_timeout_sec = st.slider("단계별 재시도 안내 시간(초)", min_value=10, max_value=60, value=30, step=5)
    gesture_threshold = st.slider("손동작 인정 기준", min_value=0.05, max_value=0.95, value=float(level_cfg["gestureThreshold"]), step=0.05, help="낮을수록 작은 손가락 굽힘도 성공으로 인정하고, 높을수록 더 분명한 손 쥐기 동작이 필요합니다.")
    target_size_scale = st.slider("물방울/공기방울/물컵 크기 보정", min_value=0.60, max_value=1.80, value=1.00, step=0.05)
    mouth_target_scale = st.slider("입 위치 목표 원 크기 보정", min_value=0.60, max_value=1.80, value=1.00, step=0.05, help="물컵을 입으로 가져가는 훈련에서 입 위치 원의 크기를 환자 상태에 맞게 조절합니다.")
    cup_position_mode = st.selectbox(
        "물컵/탁자 위치 설정",
        options=["auto_by_hand", "manual"],
        format_func=lambda v: {"auto_by_hand": "자동: 훈련 손 방향에 배치", "manual": "수동 선택"}[v],
        index=0,
        help="기본은 훈련 손의 앞쪽 아래 위치에 자동 배치하는 것이 재활 훈련 흐름에 가장 자연스럽습니다. 필요 시 수동으로 위치를 바꿀 수 있습니다.",
    )
    cup_position_preset = st.selectbox(
        "수동 위치",
        options=["left_lower", "center_lower", "right_lower"],
        format_func=lambda v: {"left_lower": "왼쪽 하단", "center_lower": "가운데 하단", "right_lower": "오른쪽 하단"}[v],
        index=2,
        disabled=(cup_position_mode != "manual"),
    )
    table_height = st.slider("탁자 높이 위치", min_value=0.76, max_value=0.94, value=0.92, step=0.01, help="값이 클수록 화면 아래쪽에 탁자가 배치됩니다.")
    speed_scale = st.slider("물방울/공기방울/물컵 속도 보정", min_value=0.00, max_value=6.00, value=1.00, step=0.25, help="0은 정지, 1은 표준 속도, 6은 빠른 이동입니다. v12에서는 속도 차이가 확실히 보이도록 비선형으로 적용됩니다.")
    st.divider()
    robustness = st.slider("손 떨림 보정/움직임 안정화", min_value=0.0, max_value=1.0, value=0.55, step=0.05)
    min_hand_conf = st.slider("손 인식 최소 신뢰도", min_value=0.20, max_value=0.80, value=0.45, step=0.05)
    use_front_camera = st.checkbox("스마트폰 전면 카메라 우선", value=True)
    mirror_view = st.checkbox("거울 모드로 보기", value=True)
    track_mouth = st.checkbox("실제 입 위치 자동 추적", value=True)
    sound_mode = st.selectbox(
        "소리 안내 방식",
        options=["audio_first", "speech_first", "tone_only", "silent"],
        format_func=lambda v: {
            "audio_first": "녹음 음성 우선 + 신호음/진동 보조",
            "speech_first": "브라우저 음성합성 우선 + 신호음/진동 보조",
            "tone_only": "신호음/진동/화면 안내만",
            "silent": "무음: 화면 안내만",
        }[v],
        index=0,
    )
    st.divider()
    st.markdown("**현재 난이도 설명**")
    st.write(level_cfg["description"])
    st.info(EXERCISES[exercise_key]["description"])

st.markdown(
    """
    **사용 순서**  
    1. 앱 안에서 **카메라 켜기**를 누르고 카메라 권한을 허용합니다.  
    2. 스마트폰/태블릿에서는 먼저 **소리 활성화/테스트**를 직접 누릅니다.  
    3. 손이 화면 중앙에 보이게 하고 **손가락 동작 보정**을 시행합니다. 보정 과정에서 손가락을 편 상태와 쥔 상태를 차례대로 인식합니다.  
    4. 보정이 완료되면 **훈련 시작**을 눌러 선택한 과제를 수행합니다.  
    """
)

config = {
    "exerciseKey": exercise_key,
    "exercise": EXERCISES[exercise_key],
    "affectedHand": affected_hand,
    "level": level,
    "levelConfig": level_cfg,
    "targetCount": int(target_count),
    "holdMs": int(hold_ms),
    "stepTimeoutMs": int(step_timeout_sec * 1000),
    "gestureThreshold": float(gesture_threshold),
    "targetSizeScale": float(target_size_scale),
    "mouthTargetScale": float(mouth_target_scale),
    "cupPositionMode": cup_position_mode,
    "cupPositionPreset": cup_position_preset,
    "tableHeight": float(table_height),
    "speedScale": float(speed_scale),
    "robustness": float(robustness),
    "minHandConfidence": float(min_hand_conf),
    "useFrontCamera": bool(use_front_camera),
    "mirrorView": bool(mirror_view),
    "trackMouth": bool(track_mouth),
    "soundMode": sound_mode,
    "audioAssets": load_audio_assets(),
    "imageAssets": load_image_assets(),
}

HTML = r'''
<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
<style>
  :root { --bg:#07111f; --panel:#111b2e; --text:#eef5ff; --muted:#b5c2d8; --green:#33d17a; --red:#ff5a6a; --blue:#57a6ff; --yellow:#ffd166; --purple:#b08cff; --cyan:#60e6ff; }
  * { box-sizing:border-box; }
  body { margin:0; background:var(--bg); color:var(--text); font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }
  .app { max-width:1180px; margin:0 auto; padding:12px; }
  .topbar { display:flex; gap:8px; flex-wrap:wrap; justify-content:space-between; align-items:center; margin-bottom:10px; }
  .title { font-weight:900; font-size:clamp(18px,3.2vw,27px); }
  .pill { border:1px solid rgba(255,255,255,.14); border-radius:999px; padding:6px 10px; color:var(--muted); font-size:13px; }
  .grid { display:grid; grid-template-columns:1fr 330px; gap:12px; }
  @media (max-width:860px) { .grid { grid-template-columns:1fr; } .sidePanel { order:2; } }
  .videoPanel { position:relative; background:#000; border-radius:18px; overflow:hidden; min-height:320px; box-shadow:0 10px 30px rgba(0,0,0,.28); }
  video { position:absolute; left:-9999px; top:-9999px; width:1px; height:1px; opacity:0; }
  canvas { width:100%; display:block; background:#06101d; aspect-ratio:4/3; }
  .cameraSizeControls { position:absolute; left:50%; bottom:10px; transform:translateX(-50%); z-index:9; display:flex; gap:7px; padding:6px; border-radius:999px; background:rgba(5,12,22,.52); border:1px solid rgba(255,255,255,.16); backdrop-filter:blur(7px); }
  .cameraSizeControls button { min-height:34px; padding:7px 11px; border-radius:999px; font-size:13px; white-space:nowrap; }
  .videoPanel.expandedCamera { position:fixed !important; inset:0 !important; width:100vw !important; height:100dvh !important; min-height:100dvh !important; z-index:99999 !important; border-radius:0 !important; background:#000; }
  .videoPanel.expandedCamera canvas { width:100vw !important; height:100dvh !important; aspect-ratio:auto !important; object-fit:contain; }
  body.landscapePreferred .videoPanel.expandedCamera { background:#000; }
  body.landscapePreferred .videoPanel.expandedCamera canvas { max-width:100vw; max-height:100dvh; }
  @media (orientation: portrait) { .videoPanel.expandedCamera .cameraSizeControls { bottom:calc(14px + env(safe-area-inset-bottom)); } }
  .videoPanel.expandedCamera .cameraSizeControls { bottom:calc(12px + env(safe-area-inset-bottom)); }
  body.cameraExpanded { overflow:hidden; }
  .overlayBanner { display:none !important; }
  #bigInstruction { font-size:clamp(21px,3.5vw,33px); font-weight:900; line-height:1.25; }
  #subInstruction { margin-top:4px; color:#d2e4ff; font-size:clamp(13px,2.3vw,17px); }
  .calOverlay { display:none; position:absolute; right:10px; top:50%; transform:translateY(-50%); flex-direction:column; align-items:center; gap:8px; padding:10px 8px; border-radius:16px; background:rgba(7,13,24,.62); border:1px solid rgba(255,255,255,.16); backdrop-filter:blur(7px); z-index:5; }
  .calOverlayTitle { writing-mode:vertical-rl; text-orientation:mixed; color:#eaf4ff; font-weight:850; font-size:12px; letter-spacing:.04em; }
  .calOverlayMeter { width:30px; height:150px; border-radius:16px; background:rgba(255,255,255,.12); border:1px solid rgba(255,255,255,.22); position:relative; overflow:hidden; }
  .calOverlayFill { position:absolute; left:0; right:0; bottom:0; height:0%; background:linear-gradient(180deg, rgba(51,209,122,.98), rgba(87,166,255,.98)); transition:height .10s linear; }
  .calOverlayPercent { color:#fff; font-weight:900; font-size:15px; text-shadow:0 1px 5px rgba(0,0,0,.5); }
  .sidePanel { background:var(--panel); border:1px solid rgba(255,255,255,.10); border-radius:18px; padding:14px; }
  .buttons { display:flex; flex-wrap:wrap; gap:8px; margin-bottom:10px; }
  button { appearance:none; border:0; border-radius:14px; padding:11px 13px; font-weight:850; background:#eaf4ff; color:#06101d; min-height:42px; cursor:pointer; }
  button.primary { background:var(--green); } button.blue { background:var(--blue); color:#fff; } button.warn { background:var(--yellow); } button.danger { background:var(--red); color:#fff; }
  .metric { display:grid; grid-template-columns:1fr auto; gap:8px; padding:9px 0; border-bottom:1px solid rgba(255,255,255,.08); font-size:15px; }
  .metric b { font-size:18px; }
  .statusBox { margin-top:10px; padding:10px; border-radius:14px; background:rgba(255,255,255,.06); min-height:88px; white-space:pre-line; color:#dceaff; font-size:14px; }
  .bar { height:13px; border-radius:999px; background:rgba(255,255,255,.12); overflow:hidden; margin-top:6px; }
  .fill { height:100%; width:0%; background:var(--green); transition:width .12s linear; }
  .calMeterRow { display:flex; gap:12px; align-items:flex-end; margin-top:10px; }
  .calMeter { width:34px; height:128px; border-radius:14px; background:rgba(255,255,255,.11); border:1px solid rgba(255,255,255,.18); position:relative; overflow:hidden; }
  .calMeterFill { position:absolute; left:0; right:0; bottom:0; height:0%; background:linear-gradient(180deg, rgba(51,209,122,.95), rgba(87,166,255,.95)); transition:height .12s linear; }
  .calMeterText { font-weight:900; font-size:18px; color:#fff; min-width:64px; }
  .small { color:var(--muted); font-size:12px; line-height:1.45; }
  .calBox { display:none; }
  a.download { display:block; margin-top:8px; color:#9fd0ff; word-break:break-all; }
</style>
</head>
<body>
<div class="app">
  <div class="topbar"><div class="title">🖐️ 손 기능 재활 가상훈련 v31</div><div class="pill" id="modeLabel">로딩 중...</div></div>
  <div class="grid">
    <div class="videoPanel">
      <video id="webcam" autoplay playsinline muted></video>
      <canvas id="outputCanvas"></canvas>
      <div class="overlayBanner"><div id="bigInstruction">① 카메라만 켜기를 누르세요</div><div id="subInstruction">카메라는 미리보기만 실행합니다. 손가락 동작 보정은 선택 사항이며, ④ 훈련 시작을 눌러야 선택한 훈련 목표가 나타납니다.</div></div>
      <div class="calOverlay" id="calOverlay"><div class="calOverlayTitle" id="calOverlayTitle">보정</div><div class="calOverlayMeter"><div class="calOverlayFill" id="calOverlayFill"></div></div><div class="calOverlayPercent" id="calOverlayPercent">0%</div></div>
      <div class="cameraSizeControls"><button id="btnCamExpand" class="blue">전체화면</button><button id="btnCamShrink">작게</button></div>
    </div>
    <div class="sidePanel">
      <div class="buttons">
        <button id="btnCameraOnly" class="primary">① 카메라만 켜기</button>
        <button id="btnSound" class="blue">② 소리 활성화/테스트</button>
        <button id="btnFingerCal" class="warn">③ 손가락 동작 보정</button>
        <button id="btnTrainStart" class="blue">④ 훈련 시작</button>
        <button id="btnAbort" class="danger">훈련 중단</button>
        <button id="btnPause">일시정지</button>
        <button id="btnStop" class="danger">카메라 정지</button>
      </div>
      <div class="metric"><span>현재 단계</span><b id="stateText">대기</b></div>
      <div class="metric"><span>성공/목표</span><b id="scoreText">0</b></div>
      <div class="metric"><span>실패 횟수</span><b id="failText">0</b></div>
      <div class="metric"><span>손동작 점수</span><b id="gestureText">0%</b></div>
      <div class="metric"><span>현재 손</span><b id="handText">-</b></div>
      <div class="metric"><span>음성 상태</span><b id="voiceStatusText">대기</b></div>
      <div class="metric"><span>성공률</span><b id="accuracyText">-</b></div>
      <div class="metric"><span>평균 반응시간</span><b id="rtText">-</b></div>
      <div class="calBox"><b>환자별 보정 상태</b><div class="small">손가락 동작 보정은 음성 안내가 끝난 뒤 ‘이제 시작하세요’ 안내 후에만 측정됩니다.</div><div class="small" id="calStatus">기본값 사용 중</div><div class="calMeterRow"><div class="calMeter"><div class="calMeterFill" id="calMeterFill"></div></div><div><div class="calMeterText" id="calPercentText">0%</div><div class="small">측정 진행률</div></div></div><div class="bar"><div class="fill" id="calFill"></div></div></div>
      <div class="statusBox" id="logBox">앱 준비 중입니다.</div><div id="downloadArea"></div>
    </div>
  </div>
</div>

<script>
let HandLandmarker = null;
let FaceLandmarker = null;
let FilesetResolver = null;
let visionModuleUrl = '';
let visionModulePromise = null;

async function loadVisionModule(){
  if(HandLandmarker && FilesetResolver) return true;
  if(visionModulePromise) return visionModulePromise;
  const candidates = [
    'https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.14/vision_bundle.mjs',
    'https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.21/vision_bundle.mjs',
    'https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.22/vision_bundle.mjs',
    'https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision/vision_bundle.mjs',
    'https://unpkg.com/@mediapipe/tasks-vision@0.10.14/vision_bundle.mjs?module'
  ];
  visionModulePromise = (async () => {
    let lastErr = null;
    for(const url of candidates){
      try{
        if(document.getElementById('modeLabel')) document.getElementById('modeLabel').textContent = 'MediaPipe 모듈 로딩 중';
        const mod = await import(/* @vite-ignore */ url);
        HandLandmarker = mod.HandLandmarker;
        FaceLandmarker = mod.FaceLandmarker || null;
        FilesetResolver = mod.FilesetResolver;
        if(!HandLandmarker || !FilesetResolver) throw new Error('HandLandmarker 또는 FilesetResolver를 찾을 수 없습니다.');
        visionModuleUrl = url;
        if(document.getElementById('modeLabel')) document.getElementById('modeLabel').textContent = 'MediaPipe 모듈 준비됨';
        return true;
      }catch(e){
        lastErr = e;
        console.warn('MediaPipe module load failed:', url, e);
      }
    }
    visionModulePromise = null;
    throw new Error('MediaPipe Hands 모듈을 불러오지 못했습니다. 네트워크, CDN 차단, 브라우저 보안 설정을 확인하세요. 마지막 오류: ' + (lastErr?.message || lastErr));
  })();
  return visionModulePromise;
}


window.addEventListener('error', (event) => {
  try{
    const msg = event?.message || '알 수 없는 오류';
    const box = document.getElementById('logBox');
    const big = document.getElementById('bigInstruction');
    const sub = document.getElementById('subInstruction');
    if(big) big.textContent = '앱 실행 중 오류가 발생했습니다';
    if(sub) sub.textContent = msg;
    if(box) box.textContent = msg;
  }catch(e){}
});
window.addEventListener('unhandledrejection', (event) => {
  try{
    const msg = String(event?.reason?.message || event?.reason || '비동기 오류');
    const box = document.getElementById('logBox');
    const big = document.getElementById('bigInstruction');
    const sub = document.getElementById('subInstruction');
    if(big) big.textContent = '모델 또는 카메라 로딩 오류';
    if(sub) sub.textContent = msg;
    if(box) box.textContent = msg;
  }catch(e){}
});

const CONFIG = __CONFIG_JSON__;
const AUDIO_ASSETS = CONFIG.audioAssets || {};
const IMAGE_ASSETS = CONFIG.imageAssets || {};
const IMG_CACHE = {};
function getSprite(name){
  const src = IMAGE_ASSETS[name];
  if(!src) return null;
  if(!IMG_CACHE[name]){ const im = new Image(); im.src = src; IMG_CACHE[name]=im; }
  return IMG_CACHE[name];
}
function drawSprite(name,x,y,w,h,alpha=1){
  const im=getSprite(name);
  if(!im || !im.complete || !im.naturalWidth) return false;
  ctx.save(); ctx.globalAlpha=alpha; ctx.drawImage(im,x-w/2,y-h/2,w,h); ctx.restore(); return true;
}
function delay(ms){ return new Promise(resolve=>setTimeout(resolve, ms)); }
function preloadSpriteImages(timeoutMs=700){
  const names=Object.keys(IMAGE_ASSETS||{});
  if(!names.length) return Promise.resolve();
  return new Promise(resolve=>{
    let left=names.length;
    const done=()=>{ left--; if(left<=0){ clearTimeout(timer); resolve(); } };
    const timer=setTimeout(resolve, timeoutMs);
    for(const name of names){
      const im=getSprite(name);
      if(!im){ done(); continue; }
      if(im.complete && im.naturalWidth){ done(); continue; }
      const prevLoad=im.onload, prevErr=im.onerror;
      im.onload=(e)=>{ try{ if(prevLoad) prevLoad.call(im,e); }catch(_){} done(); };
      im.onerror=(e)=>{ try{ if(prevErr) prevErr.call(im,e); }catch(_){} done(); };
    }
  });
}
const video = document.getElementById('webcam');
const canvas = document.getElementById('outputCanvas');
const ctx = canvas.getContext('2d');
const ui = {
  modeLabel: document.getElementById('modeLabel'), big: document.getElementById('bigInstruction'), sub: document.getElementById('subInstruction'), state: document.getElementById('stateText'), score: document.getElementById('scoreText'), fail: document.getElementById('failText'), gesture: document.getElementById('gestureText'), hand: document.getElementById('handText'), voice: document.getElementById('voiceStatusText'), accuracy: document.getElementById('accuracyText'), rt: document.getElementById('rtText'), log: document.getElementById('logBox'), calStatus: document.getElementById('calStatus'), calFill: document.getElementById('calFill'), calMeterFill: document.getElementById('calMeterFill'), calPercent: document.getElementById('calPercentText'), downloadArea: document.getElementById('downloadArea'), calOverlay: document.getElementById('calOverlay'), calOverlayFill: document.getElementById('calOverlayFill'), calOverlayPercent: document.getElementById('calOverlayPercent'), calOverlayTitle: document.getElementById('calOverlayTitle'), videoPanel: document.querySelector('.videoPanel')
};
const btn = { camera:document.getElementById('btnCameraOnly'), sound:document.getElementById('btnSound'), fingerCal:document.getElementById('btnFingerCal'), train:document.getElementById('btnTrainStart'), abort:document.getElementById('btnAbort'), pause:document.getElementById('btnPause'), stop:document.getElementById('btnStop'), expand:document.getElementById('btnCamExpand'), shrink:document.getElementById('btnCamShrink') };

const messages = {
  sound_test:'소리 안내가 활성화되었습니다.',
  app_intro:'앱 사용 순서를 안내합니다. 카메라만 켜기를 누른 뒤, 필요하면 손가락 동작 보정을 합니다. 훈련 시작을 누르면 선택한 과제 안내가 끝난 뒤 훈련이 시작됩니다.',
  start_camera:'카메라만 켜졌습니다. 지금은 훈련 전 준비 상태입니다. 필요하면 손가락 동작 보정 버튼을 누르세요. 보정을 하지 않고 훈련 시작 버튼을 누르면 자동 손동작 기준으로 훈련합니다.',
  hand_not_found:'손이 보이지 않습니다. 손 전체가 화면에 들어오도록 조정하세요.',
  wrong_hand:'선택한 손이 아닙니다. 훈련 손을 다시 확인하세요.',
  low_quality:'손 인식이 불안정합니다. 조명을 밝게 하고 손 가림을 줄여 주세요.',
  finger_cal_open:'손가락 동작 보정을 시작합니다. 먼저 손가락을 최대한 펴는 단계입니다. 설명이 끝난 뒤 이제 시작하세요라는 안내가 나오면, 그때부터 손가락을 최대한 편 상태로 유지해 주세요.',
  finger_cal_close:'이번에는 손가락을 최대한 구부려 손을 쥐는 단계입니다. 설명이 끝난 뒤 이제 시작하세요라는 안내가 나오면, 그때부터 손가락을 최대한 구부린 상태로 유지해 주세요.',
  finger_cal_done:'굽힘 동작이 인식되었습니다. 손가락 동작 보정이 완료되었습니다. 손 인식 표시선을 잠시 숨깁니다. 이제 훈련 시작 버튼을 눌러 선택한 훈련을 시작하세요.',
  cal_done:'보정이 완료되었습니다.',
  seek_target:'목표 위치로 손을 가져가세요.',
  now_gesture: CONFIG.exercise.gesture==='pinch' ? '엄지와 검지를 맞대어 집으세요.' : (CONFIG.exercise.gesture==='open' ? '손을 충분히 펴세요.' : '손을 쥐세요.'),
  hold_gesture:'좋습니다. 끝동작을 그대로 유지하세요.',
  success:'정상적으로 성공했습니다.',
  complete:'모든 훈련이 끝났습니다. 결과를 확인하세요.',
  cup_reach:'물컵으로 손을 가져가세요.',
  cup_grasp:'물컵을 잡으세요. 손을 쥔 상태를 유지하세요.',
  cup_to_mouth:'좋습니다. 물이 담긴 컵을 실제 입 위치까지 천천히 옮기세요.',
  cup_drink_hold:'입 위치에 도착했습니다. 그 위치에서 잠시 멈추세요. 물을 마신 뒤 빈 컵을 다시 탁자 위치로 옮기게 됩니다.',
  mouth_not_found:'입 위치가 보이지 않습니다. 얼굴과 입이 화면에 보이도록 조정하세요.',
  air_bubble_seek:'얼굴 아래에 퍼져 있는 물방울 중 하나로 손을 천천히 가져가세요.',
  air_bubble_grasp:'물방울 안에서 손을 쥐세요. 손을 쥔 상태를 잠시 유지하면 물방울이 터집니다.',
  air_bubble_hold:'좋습니다. 물방울을 잡은 상태를 잠시 유지하세요.',
  pause:'훈련을 일시정지합니다.',
  resume:'훈련을 다시 시작합니다.',
  training_start:'훈련을 시작합니다. 화면 안내와 음성 안내에 따라 선택한 과제를 수행하세요.',
  training_abort:'훈련을 중단했습니다. 음성 안내도 중단했습니다. 카메라는 켜진 상태입니다. 다른 옵션을 선택하거나 훈련 시작 버튼을 눌러 다시 시작하세요.'
};

let handLandmarker=null, faceLandmarker=null, stream=null, running=false, cameraOnlyReady=false, trainingActive=false, trainingPreviewActive=false, paused=false, animationId=null, lastVideoTime=-1;
let audioCtx=null, soundUnlocked=false, lastSpeakKey='', lastSpeakAt=0, activeAudio=null;
let speechQueue=[], speechActive=false, speechMaxQueue=12, selectedKoreanVoice=null, speechGeneration=0;
let lastStageSpeechKey='', lastStageSpeechAt=0;
let trainingRunId=0;
let state='idle', score=0, attempts=0, successes=0, failureCount=0, reactionTimes=[], successTimes=[], gameStartTime=0;
let target=null, stage='none', holdStart=null, overlapStart=null, reactionStart=null, lastStatusVoice=0;
let targetSerial=0, lastStepId='', stepStartedAt=0, lastFailureAt=0;
let bubbleOpenReady=false, bubbleOpenStart=0, bubbleCandidateId=null;
let openMetrics=null, closeMetrics=null, calMode=null, calSamples=[], calStart=0, calVoiceMilestone=-1, combinedCalActive=false, calDurationMs=3000, calStepId=0, calWaitingForStart=false, calPrepTimer=null, calPrepEnd=0, calPrepMode=null;
let hideHandLandmarksUntil=0;
let smoothLandmarks=null, smoothedGesture=0, smoothedCursor=null, lastHandFoundAt=0, neutralTilt=null;
let currentMouth=null, smoothedMouth=null, mouthDetectedAt=0, lastMouthVoice=0, successLock=false;
let particles=[];

ui.modeLabel.textContent = `v29 준비됨 · ${CONFIG.exercise.label} · ${CONFIG.levelConfig.name}`;

function now(){ return performance.now(); }
function clamp(v,lo,hi){ return Math.max(lo,Math.min(hi,v)); }
function dist(a,b){ return Math.hypot(a.x-b.x,a.y-b.y); }
function lerp(a,b,t){ return a+(b-a)*t; }
function mean(arr){ return arr.length ? arr.reduce((a,b)=>a+b,0)/arr.length : 0; }

function setInstruction(big, sub='', kind='info'){
  ui.big.textContent=big; ui.sub.textContent=sub;
  ui.big.style.color = kind==='bad'?'#ff8e9a':kind==='ready'?'#33d17a':kind==='action'?'#57a6ff':kind==='warn'?'#ffd166':kind==='drink'?'#60e6ff':'#fff';
}
function log(msg){ ui.log.textContent=msg; }

function updateVoiceStatus(text){ if(ui.voice) ui.voice.textContent=text; }
function clearCalibrationTimers(){ try{ if(calPrepTimer){ clearInterval(calPrepTimer); calPrepTimer=null; } }catch(e){} calPrepEnd=0; calPrepMode=null; }
function stopAllSpeech(status='음성 중단'){
  clearCalibrationTimers();
  speechGeneration++;
  try{ calStepId++; }catch(e){}
  speechQueue=[];
  speechActive=false;
  lastSpeakKey='';
  lastSpeakAt=0;
  try{ if(activeAudio){ activeAudio.pause(); activeAudio.currentTime=0; activeAudio=null; } }catch(e){}
  try{ if('speechSynthesis' in window){ window.speechSynthesis.cancel(); window.speechSynthesis.resume(); } }catch(e){}
  updateVoiceStatus(status);
}

function cancelSpeechPlaybackOnly(status='단계 안내 전환'){
  speechGeneration++;
  speechQueue=[];
  speechActive=false;
  lastSpeakKey='';
  lastSpeakAt=0;
  try{ if(activeAudio){ activeAudio.pause(); activeAudio.currentTime=0; activeAudio=null; } }catch(e){}
  try{ if('speechSynthesis' in window){ window.speechSynthesis.cancel(); window.speechSynthesis.resume(); } }catch(e){}
  updateVoiceStatus(status);
}
function speakStagePrompt(key, text, force=false, minGapMs=5200){
  const t=now();
  if(!force && key===lastStageSpeechKey && t-lastStageSpeechAt<minGapMs) return false;
  lastStageSpeechKey=key; lastStageSpeechAt=t;
  cancelSpeechPlaybackOnly('단계 안내 전환');
  return speakTextNoScreen(key, text, true);
}
function beginSilentHold(){ if(!holdStart) holdStart=now(); }
function resetSessionForNewAction(status='새 작업'){
  stopAllSpeech(status);
  trainingRunId++;
  calStepId++;
  calWaitingForStart=false;
  trainingPreviewActive=false;
  lastStageSpeechKey=''; lastStageSpeechAt=0;
}
function selectedTaskIntroBrief(){
  const t=CONFIG.exercise.taskType;
  if(t==='cup_drink') return '현재 선택된 과제는 물컵 마시기입니다. 컵을 쥐고 입 위치로 옮긴 뒤, 빈 컵을 다시 탁자 위 원래 위치에 놓습니다.';
  if(t==='hand_bubbles') return '현재 선택된 과제는 공기방울 잡기입니다. 방울 안에서 먼저 손을 펴고, 그 다음 같은 방울 안에서 손을 쥡니다.';
  if(CONFIG.exercise.gesture==='pinch') return '현재 선택된 과제는 작은 물방울 집기입니다. 검지 끝을 목표에 맞춘 뒤 엄지와 검지를 맞댑니다.';
  if(CONFIG.exercise.gesture==='open') return '현재 선택된 과제는 손 펴기입니다. 목표 위에서 손가락을 충분히 폅니다.';
  return '선택한 과제를 수행합니다.';
}
function appIntroText(){ return `${messages.app_intro} ${selectedTaskIntroBrief()}`; }
function announceAppIntro(force=false){ if(!force && !soundUnlocked) return; speakText('app_intro', appIntroText(), true); }

function pickKoreanVoice(){
  if(!('speechSynthesis' in window)) return null;
  const voices = window.speechSynthesis.getVoices ? window.speechSynthesis.getVoices() : [];
  if(!voices || voices.length===0) return null;
  selectedKoreanVoice = voices.find(v => (v.lang||'').toLowerCase().startsWith('ko')) || voices.find(v => /korean|한국|ko/i.test((v.name||'')+' '+(v.lang||''))) || voices[0];
  return selectedKoreanVoice;
}
function splitSpeechText(text){
  const raw = String(text||'').replace(/\s+/g,' ').trim();
  if(!raw) return [];
  const sents = raw.match(/[^.!?。！？]+[.!?。！？]?/g) || [raw];
  const chunks=[]; let buf='';
  for(const s of sents){
    const part=s.trim(); if(!part) continue;
    if((buf+' '+part).trim().length>95){ if(buf) chunks.push(buf.trim()); buf=part; }
    else buf=(buf+' '+part).trim();
  }
  if(buf) chunks.push(buf.trim());
  return chunks.length?chunks:[raw];
}
function primeSpeechSynthesis(){
  if(!('speechSynthesis' in window)){ updateVoiceStatus('음성합성 없음'); return false; }
  try{
    window.speechSynthesis.resume();
    const voice=pickKoreanVoice();
    updateVoiceStatus(voice ? `음성 준비: ${voice.lang || 'voice'}` : '음성 준비 중');
    return true;
  }catch(e){ updateVoiceStatus('음성 준비 실패'); return false; }
}
function makeUtterance(text, key='voice'){
  const u=new SpeechSynthesisUtterance(String(text||''));
  u.lang='ko-KR'; u.rate=.80; u.pitch=1.0; u.volume=1.0;
  const voice=pickKoreanVoice();
  if(voice) u.voice=voice;
  u.onstart=()=>updateVoiceStatus('음성 안내 중');
  u.onerror=(e)=>{ console.warn('speech error',e); updateVoiceStatus('음성 오류'); toneFor(key); };
  return u;
}
function directSpeak(text, key='voice'){
  if(CONFIG.soundMode==='silent' || CONFIG.soundMode==='tone_only') return false;
  if(!('speechSynthesis' in window)){ updateVoiceStatus('음성합성 없음'); return false; }
  try{
    window.speechSynthesis.cancel();
    speechQueue=[]; speechActive=false;
    window.speechSynthesis.resume();
    const u=makeUtterance(text,key);
    u.onend=()=>{ speechActive=false; updateVoiceStatus('활성화됨'); setTimeout(drainSpeechQueue,160); };
    speechActive=true;
    window.speechSynthesis.speak(u);
    setTimeout(()=>{ try{ window.speechSynthesis.resume(); }catch(e){} },350);
    setTimeout(()=>{ try{ window.speechSynthesis.resume(); }catch(e){} },1200);
    return true;
  }catch(e){ console.warn('directSpeak failed',e); updateVoiceStatus('음성 실패'); toneFor(key); return false; }
}
if('speechSynthesis' in window){
  window.speechSynthesis.onvoiceschanged = () => { pickKoreanVoice(); updateVoiceStatus(selectedKoreanVoice ? `음성 준비: ${selectedKoreanVoice.lang || 'voice'}` : '음성 준비'); };
}


async function unlockAudio(testVoice=true){
  try{
    audioCtx = audioCtx || new (window.AudioContext||window.webkitAudioContext)();
    if(audioCtx.state==='suspended') await audioCtx.resume();
    soundUnlocked=true;
    primeSpeechSynthesis();
    beep(660,.08,.06); setTimeout(()=>beep(880,.08,.06),110);
    setInstruction('소리 안내가 활성화되었습니다','훈련 설명과 단계 안내가 음성으로 출력됩니다. 들리지 않으면 미디어 볼륨과 무음모드를 확인하세요.','ready');
    if(testVoice){
      const ok = directSpeak('소리 안내가 활성화되었습니다. ' + appIntroText(), 'sound_test');
      if(!ok) speakText('sound_test','소리 안내가 활성화되었습니다. ' + appIntroText(),true);
      updateVoiceStatus(ok?'음성 테스트 중':'활성화됨');
    }else{
      updateVoiceStatus('활성화됨');
    }
  }catch(e){ updateVoiceStatus('차단됨'); setInstruction('소리 활성화가 제한되었습니다','무음모드, 미디어 볼륨, 브라우저 자동재생 제한을 확인하세요.','warn'); }
}
function beep(freq=660,duration=.12,vol=.08){
  if(CONFIG.soundMode==='silent') return;
  try{ audioCtx=audioCtx||new (window.AudioContext||window.webkitAudioContext)(); const osc=audioCtx.createOscillator(); const gain=audioCtx.createGain(); osc.frequency.value=freq; gain.gain.value=vol; osc.connect(gain); gain.connect(audioCtx.destination); osc.start(); osc.stop(audioCtx.currentTime+duration);}catch(e){}
}
function toneFor(key){
  if(CONFIG.soundMode==='silent') return;
  if(key==='success' || key.startsWith('rep_success')){beep(740,.08,.08); setTimeout(()=>beep(980,.10,.08),110);} else if(key==='complete'){beep(660,.08,.08); setTimeout(()=>beep(880,.08,.08),110); setTimeout(()=>beep(1100,.12,.08),230);} else if(['wrong_hand','hand_not_found','low_quality'].includes(key) || key.startsWith('fail')){beep(220,.16,.09); setTimeout(()=>beep(180,.16,.09),190);} else if(['now_gesture','cup_grasp','air_bubble_grasp'].includes(key) || key.startsWith('stage')){beep(880,.12,.08);} else {beep(600,.08,.05);}
}
function speakOnce(key, force=false){
  const text=messages[key]||key;
  speakText(key, text, force);
}
function speakTextInternal(key, text, force=false, showOnScreen=true){
  const t=now();
  if(!force && key===lastSpeakKey && t-lastSpeakAt<6200) return false;
  lastSpeakKey=key; lastSpeakAt=t;
  if(showOnScreen) ui.sub.textContent=text;
  if(navigator.vibrate){
    if(['success','complete'].includes(key) || key.startsWith('rep_success')) navigator.vibrate([70,40,70]);
    else if(['wrong_hand','hand_not_found','low_quality'].includes(key) || key.startsWith('fail')) navigator.vibrate([140,60,140]);
    else navigator.vibrate(45);
  }
  playMessage(key,text);
  return true;
}
function speakText(key, text, force=false){
  return speakTextInternal(key, text, force, true);
}
function speakTextNoScreen(key, text, force=false){
  return speakTextInternal(key, text, force, false);
}
function estimateSpeechDurationMs(text){
  if(CONFIG.soundMode==='silent' || CONFIG.soundMode==='tone_only') return 900;
  const len=String(text||'').replace(/\s+/g,'').length;
  // Korean browser speech synthesis can lag on mobile devices.
  // Use a conservative duration so callbacks never start measurement while guidance is still speaking.
  return clamp(2400 + len*190, 4200, 30000);
}
function waitForSpeechCompletion(text, callback, generation, minExtraMs=350){
  const started=now();
  const minWait=estimateSpeechDurationMs(text) + minExtraMs;
  const maxWait=Math.max(minWait+3500, 8000);
  const tick=()=>{
    if(generation!==speechGeneration) return;
    const elapsed=now()-started;
    const speaking = !!(window.speechSynthesis && window.speechSynthesis.speaking);
    const pending = speechActive || speechQueue.length>0 || speaking;
    // Do not trust early speechSynthesis end events on mobile; the minimum wait is always enforced.
    if(elapsed < minWait){ setTimeout(tick, 180); return; }
    if(!pending || elapsed>=maxWait){
      if(typeof callback==='function') callback();
      return;
    }
    setTimeout(tick, 180);
  };
  setTimeout(tick, 180);
}
function speakTextWithCallback(key, text, force=false, callback=null, showOnScreen=true){
  if(showOnScreen) speakText(key, text, force); else speakTextNoScreen(key, text, force);
  const myGen=speechGeneration;
  if(CONFIG.soundMode==='silent' || CONFIG.soundMode==='tone_only' || !soundUnlocked){
    const delay=estimateSpeechDurationMs(text) + 400;
    setTimeout(()=>{ if(myGen===speechGeneration && typeof callback==='function') callback(); }, delay);
    return;
  }
  waitForSpeechCompletion(text, callback, myGen, 500);
}
function setCalProgress(pct){
  const p=clamp(pct,0,1);
  const pctText=`${Math.round(p*100)}%`;
  if(ui.calFill) ui.calFill.style.width=pctText;
  if(ui.calMeterFill) ui.calMeterFill.style.height=pctText;
  if(ui.calPercent) ui.calPercent.textContent=pctText;
  if(ui.calOverlayFill) ui.calOverlayFill.style.height=pctText;
  if(ui.calOverlayPercent) ui.calOverlayPercent.textContent=pctText;
  const show = !!(combinedCalActive || calMode || stage==='calibration_instruction' || stage==='calibration_measure');
  if(ui.calOverlay) ui.calOverlay.style.display = show ? 'flex' : 'none';
}
function setCalOverlayLabel(label){ if(ui.calOverlayTitle) ui.calOverlayTitle.textContent=label || '보정'; }
function resetCalProgress(){ setCalProgress(0); }
function playCalibrationBeepDone(){ beep(740,.08,.08); setTimeout(()=>beep(980,.10,.08),120); }
function playMessage(key,text){
  if(CONFIG.soundMode==='silent') return;
  if(!soundUnlocked){ toneFor(key); return; }
  const asset=AUDIO_ASSETS[key];
  if(CONFIG.soundMode==='audio_first' && asset && asset.data){ try{ if(activeAudio){ activeAudio.pause(); activeAudio.currentTime=0; } activeAudio=new Audio(asset.data); activeAudio.onended=()=>{ activeAudio=null; }; activeAudio.play().catch(()=>fallbackSpeechOrTone(text,key)); return; }catch(e){} }
  fallbackSpeechOrTone(text,key);
}
function fallbackSpeechOrTone(text,key){
  if(CONFIG.soundMode==='tone_only' || !('speechSynthesis' in window)){ toneFor(key); updateVoiceStatus('신호음'); return; }
  try{ enqueueSpeech(text,key); }catch(e){ toneFor(key); updateVoiceStatus('음성 실패'); }
}
function enqueueSpeech(text,key){
  const gen=speechGeneration;
  const important = key.startsWith('task_intro') || key.startsWith('task_begin') || key.startsWith('complete') || key.startsWith('fail') || key.startsWith('finger_cal') || key.startsWith('training') || key==='sound_test';
  if(important){
    window.speechSynthesis?.cancel?.();
    speechActive=false;
    speechQueue = [];
  }else if(speechQueue.length >= speechMaxQueue){
    speechQueue = speechQueue.slice(-speechMaxQueue+1);
  }
  const parts = splitSpeechText(text);
  parts.forEach((part,idx)=>speechQueue.push({text:part,key:idx===0?key:`${key}_part${idx}`, gen}));
  drainSpeechQueue();
}
function drainSpeechQueue(){
  if(speechActive || speechQueue.length===0) return;
  const item = speechQueue.shift();
  if(item.gen !== speechGeneration){ speechActive=false; setTimeout(drainSpeechQueue,0); return; }
  speechActive = true;
  try{
    if(!soundUnlocked){ speechActive=false; toneFor(item.key); return; }
    window.speechSynthesis.resume();
    const u=makeUtterance(item.text, item.key);
    let doneCalled=false;
    const done=()=>{ if(doneCalled) return; doneCalled=true; speechActive=false; if(item.gen===speechGeneration){ updateVoiceStatus(speechQueue.length?`안내 중 ${speechQueue.length}`:'활성화됨'); setTimeout(drainSpeechQueue,120); } };
    u.onstart=()=>updateVoiceStatus('음성 안내 중');
    u.onend=done;
    u.onerror=(e)=>{ console.warn('speech error',e); toneFor(item.key); updateVoiceStatus('음성 오류'); done(); };
    window.speechSynthesis.speak(u);
    setTimeout(()=>{ try{ window.speechSynthesis.resume(); }catch(e){} },700);
    setTimeout(()=>{ if(speechActive && !window.speechSynthesis.speaking){ toneFor(item.key); done(); } },4500);
  }catch(e){ speechActive=false; toneFor(item.key); updateVoiceStatus('음성 실패'); drainSpeechQueue(); }
}

async function startCameraOnly(){
  resetSessionForNewAction('카메라 준비');
  if(running){
    setInstruction('카메라가 이미 켜져 있습니다','보정을 완료한 뒤 훈련 시작 버튼을 누르세요.','ready');
    return;
  }
  try{
    if(!soundUnlocked && CONFIG.soundMode!=='silent') await unlockAudio(false);
    setInstruction('카메라와 모델을 준비합니다','MediaPipe Hands 모듈과 모델을 불러오는 중입니다. 잠시 기다려 주세요.','info');
    log('카메라만 켜기 버튼이 눌렸습니다. MediaPipe Hands 모듈을 불러오는 중입니다. 훈련은 아직 시작하지 않습니다.');
    await loadVisionModule();
    const wasmBase = visionModuleUrl
      ? visionModuleUrl.replace(/vision_bundle\.mjs(?:\?module)?$/, 'wasm')
      : 'https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.14/wasm';
    const vision = await FilesetResolver.forVisionTasks(wasmBase);
    const handOptions = (delegate) => ({
      baseOptions:{
        modelAssetPath:'https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task',
        delegate
      },
      runningMode:'VIDEO',
      numHands:2,
      minHandDetectionConfidence:CONFIG.minHandConfidence,
      minHandPresenceConfidence:CONFIG.minHandConfidence,
      minTrackingConfidence:CONFIG.minHandConfidence
    });
    try{
      ui.modeLabel.textContent='손 모델 로딩 중: GPU';
      handLandmarker = await HandLandmarker.createFromOptions(vision, handOptions('GPU'));
    }catch(gpuErr){
      console.warn('GPU delegate failed. Fallback to CPU.', gpuErr);
      ui.modeLabel.textContent='손 모델 로딩 중: CPU';
      handLandmarker = await HandLandmarker.createFromOptions(vision, handOptions('CPU'));
    }
    faceLandmarker = null;
    if(CONFIG.trackMouth && FaceLandmarker){
      const faceOptions = (delegate) => ({
        baseOptions:{
          modelAssetPath:'https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/latest/face_landmarker.task',
          delegate
        },
        runningMode:'VIDEO',
        numFaces:1,
        minFaceDetectionConfidence:0.35,
        minFacePresenceConfidence:0.35,
        minTrackingConfidence:0.35
      });
      try{
        ui.modeLabel.textContent='입 위치 추적 모델 로딩 중: GPU';
        faceLandmarker = await FaceLandmarker.createFromOptions(vision, faceOptions('GPU'));
      }catch(faceGpuErr){
        console.warn('Face GPU delegate failed. Fallback to CPU.', faceGpuErr);
        try{
          ui.modeLabel.textContent='입 위치 추적 모델 로딩 중: CPU';
          faceLandmarker = await FaceLandmarker.createFromOptions(vision, faceOptions('CPU'));
        }catch(faceErr){
          console.warn('FaceLandmarker failed. Mouth target will use fallback position.', faceErr);
          faceLandmarker = null;
        }
      }
    }
    ui.modeLabel.textContent='카메라 권한 요청 중';
    stream = await navigator.mediaDevices.getUserMedia({ video:{ facingMode:CONFIG.useFrontCamera?'user':'environment', width:{ideal:960}, height:{ideal:720}, frameRate:{ideal:24,max:30}}, audio:false });
    video.srcObject=stream; await video.play();
    canvas.width=video.videoWidth||960; canvas.height=video.videoHeight||720;
    running=true; cameraOnlyReady=true; trainingActive=false; trainingPreviewActive=false; paused=false; target=null; particles=[]; stage='camera_only_ready'; state='camera_only_ready'; holdStart=null; updateUI();
    speakText('camera_ready_sequence', `카메라가 켜졌습니다. 지금은 훈련 전 준비 상태입니다. 필요하면 손가락 동작 보정 버튼을 누르세요. 훈련 시작 버튼을 누르면 ${selectedTaskIntroBrief()} 안내 후 목표가 나타납니다.`, true);
    setInstruction('카메라만 켜졌습니다','선택: ③ 손가락 동작 보정 또는 ④ 훈련 시작. 보정을 하지 않아도 자동 기준으로 훈련할 수 있습니다.','ready');
    log('카메라만 켜졌습니다. 아직 훈련은 시작되지 않았습니다. 이 상태에서는 선택한 훈련 목표를 생성하지 않습니다. 손가락 동작 보정은 선택 사항이며, ④ 훈련 시작을 누르면 자동 또는 보정 기준으로 시작합니다.');
    preloadSpriteImages(900);
    renderLoop();
  }catch(e){ console.error(e); setInstruction('카메라 또는 모델을 시작할 수 없습니다','HTTPS 접속, 카메라 권한, 브라우저를 확인하세요.','bad'); log(String(e)); }
}
function stopApp(){
  resetSessionForNewAction('카메라 정지');
  running=false; cameraOnlyReady=false; trainingActive=false; trainingPreviewActive=false; paused=false; calMode=null; target=null; particles=[];
  if(animationId) cancelAnimationFrame(animationId);
  if(stream) stream.getTracks().forEach(t=>t.stop());
  stream=null; state='idle'; stage='idle';
  setInstruction('카메라가 정지되었습니다','다시 시작하려면 ① 카메라만 켜기 버튼을 누르세요.','info');
  updateUI();
}
async function startTraining(){
  if(!running || !cameraOnlyReady){
    resetSessionForNewAction('훈련 시작');
    setInstruction('먼저 ① 카메라만 켜기를 누르세요','카메라 미리보기와 손 인식이 준비된 뒤 보정과 훈련을 진행하세요.','warn');
    speakText('need_camera_train','먼저 카메라만 켜기 버튼을 누르세요. 카메라가 켜진 뒤 보정과 훈련을 시작할 수 있습니다.',true);
    return;
  }
  // 보정 중에는 훈련 시작이 보정을 끊지 않도록, 세션 초기화보다 먼저 차단합니다.
  if(combinedCalActive || calMode || calWaitingForStart){
    setInstruction('보정이 진행 중입니다','손가락 동작 보정이 완전히 끝난 뒤 ④ 훈련 시작 버튼을 누르세요.','warn');
    return;
  }
  resetSessionForNewAction('훈련 시작');
  const run=trainingRunId;
  paused=false;
  trainingActive=false;
  holdStart=null; successLock=false;

  // 1) 목표물을 먼저 만들고 즉시 카메라 화면에 그립니다.
  prepareGamePreview();
  await preloadSpriteImages(900);
  forcePreviewDraw();
  await delay(180);

  // 2) 목표물이 보이는 상태에서 짧은 안내를 출력합니다. 이 동안에는 아직 성공/실패 판정하지 않습니다.
  const intro = conciseTrainingIntroText();
  setInstruction('목표 확인','', 'ready');
  speakTextWithCallback('task_intro_'+run, intro, true, ()=>{
    if(run!==trainingRunId || !running || paused || combinedCalActive) return;
    forcePreviewDraw();
    speakTextWithCallback('training_start_now_'+run, '목표를 확인하세요. 시작하세요.', true, ()=>{
      if(run!==trainingRunId || !running || paused || combinedCalActive) return;
      activatePreparedGame();
    }, false);
  }, false);
}

function abortTraining(){
  resetSessionForNewAction('훈련 중단');
  if(!running){ setInstruction('카메라가 꺼져 있습니다','① 카메라만 켜기 버튼으로 다시 시작할 수 있습니다.','info'); return; }
  trainingActive=false; trainingPreviewActive=false; paused=false; calMode=null; target=null; particles=[]; stage='camera_only_ready'; state='camera_only_ready'; holdStart=null; overlapStart=null; reactionStart=null; successLock=false; resetBubbleOpenGate(); updateUI();
  setInstruction('훈련을 중단했습니다','음성 안내와 선택한 훈련 과제를 모두 중단했습니다. 카메라는 켜진 상태입니다. 보정 또는 훈련 시작을 다시 선택하세요.','warn');
  speakText('training_abort_now', '훈련을 중단했습니다. 음성 안내도 중단했습니다. 카메라는 켜진 상태입니다. 필요하면 보정을 다시 하거나 훈련 시작 버튼을 눌러 다시 시작하세요.', true);
}
function prepareGamePreview(){
  trainingActive=false; trainingPreviewActive=true; paused=false;
  score=0; attempts=0; successes=0; failureCount=0; reactionTimes=[]; successTimes=[];
  target=null; stage='none'; holdStart=null; overlapStart=null; reactionStart=null; particles=[];
  gameStartTime=now(); state='training_preview'; ui.downloadArea.innerHTML=''; neutralTilt=null; successLock=false;
  targetSerial=0; lastStepId=''; stepStartedAt=now(); lastFailureAt=0; lastStatusVoice=now(); resetBubbleOpenGate();
  updateUI();
  spawnTaskTarget();
  setInstruction('목표 확인','', 'ready');
  forcePreviewDraw();
  updateUI();
}
function forcePreviewDraw(){
  try{
    if(canvas && canvas.width && canvas.height){ drawScene(null,null); updateUI(); }
  }catch(e){ console.warn('preview draw failed', e); }
}
function activatePreparedGame(){
  if(!target) spawnTaskTarget();
  trainingPreviewActive=false; trainingActive=true; paused=false;
  gameStartTime=now(); reactionStart=now(); stepStartedAt=now(); holdStart=null; overlapStart=null; successLock=false; lastStatusVoice=now();
  lastStageSpeechKey=''; lastStageSpeechAt=0; setInstruction('훈련 시작','목표를 보고 천천히 시작하세요.', 'ready');
  updateUI();
}
function resetGame(announce=true){
  trainingPreviewActive=false; trainingActive=true; paused=false;
  score=0; attempts=0; successes=0; failureCount=0; reactionTimes=[]; successTimes=[]; target=null; stage='none'; holdStart=null; overlapStart=null; reactionStart=null; particles=[]; gameStartTime=now(); state='waiting_hand'; ui.downloadArea.innerHTML=''; neutralTilt=null; successLock=false; targetSerial=0; lastStepId=''; stepStartedAt=now(); lastFailureAt=0; resetBubbleOpenGate(); updateUI(); spawnTaskTarget();
  if(announce){
    speakTextNoScreen('task_intro_'+targetSerial, taskIntroText(), true);
  }
}
function gestureActionText(){
  if(CONFIG.exercise.gesture==='pinch') return '엄지와 검지를 맞대어 집기 동작을 하세요';
  if(CONFIG.exercise.gesture==='open') return '손을 충분히 펴세요';
  return '손을 쥐세요';
}
function taskIntroText(){
  if(CONFIG.exercise.taskType==='hand_bubbles'){
    return `${calibrationRequiredNotice()} 공기방울 잡기 훈련입니다. 방울 안에서 먼저 손을 펴고, 그 다음 같은 방울 안에서 손을 쥐세요.`;
  }
  return `${CONFIG.exercise.label} 훈련입니다. ${taskStartText()}`;
}
function conciseTrainingIntroText(){
  const t=CONFIG.exercise.taskType;
  if(t==='cup_drink') return '물컵 마시기 훈련입니다. 컵을 쥐고 입 위치로 옮긴 뒤, 빈 컵을 원래 위치에 놓습니다.';
  if(t==='hand_bubbles') return '공기방울 잡기 훈련입니다. 방울 안에서 먼저 손을 펴고, 그 다음 같은 방울 안에서 손을 쥡니다.';
  if(CONFIG.exercise.gesture==='pinch') return '작은 물방울 집기 훈련입니다. 검지 끝을 맞추고 엄지와 검지를 맞댑니다.';
  if(CONFIG.exercise.gesture==='open') return '손 펴기 훈련입니다. 목표 위에서 손가락을 충분히 폅니다.';
  return '훈련을 시작합니다. 안내 후 시작합니다.';
}
function taskStartText(){
  const rep=Math.min(score+1, CONFIG.targetCount);
  const t=CONFIG.exercise.taskType;
  if(t==='cup_drink') return `${rep}회차입니다. 먼저 탁자 위 물컵으로 손을 가져가세요. 컵을 잡은 뒤 실제 입 위치까지 옮기고 잠시 멈춥니다. 물이 사라지면 빈 컵을 다시 원래 탁자 위치에 놓으세요.`;
  if(t==='hand_bubbles') return `남은 방울 중 하나로 손을 천천히 이동하세요. 방울 안에 들어가면 먼저 손을 펴고, 그 다음 같은 방울 안에서 손가락을 굽혀 쥡니다.`;
  return `${rep}회차입니다. 손을 ${CONFIG.exercise.targetName} 위치로 가져간 뒤, ${gestureActionText()}. 끝동작은 잠시 유지합니다.`;
}
function taskStartMessage(){ const t=CONFIG.exercise.taskType; if(t==='cup_drink') return 'cup_reach'; if(t==='hand_bubbles') return 'air_bubble_seek'; return 'seek_target'; }

function metricText(v){ return Number.isFinite(v) ? v.toFixed(2) : '-'; }
function calibrationSummary(){
  const openText = openMetrics ? `손 편 기준 ${metricText(openMetrics.fingertipAvg)}` : '손 편 기준 미보정(자동 기준 사용 가능)';
  const closeText = closeMetrics ? `쥔 기준 ${metricText(closeMetrics.fingertipAvg)}` : '쥔 기준 미보정(자동 기준 사용 가능)';
  const rangeText = (openMetrics && closeMetrics) ? ` · 기준 범위 ${metricText(openMetrics.fingertipAvg-closeMetrics.fingertipAvg)}` : '';
  const warning = (openMetrics && closeMetrics && openMetrics.fingertipAvg <= closeMetrics.fingertipAvg + 0.08) ? ' · 기준 차이가 작습니다. 보정을 다시 권장합니다.' : '';
  return `${openText} / ${closeText}${rangeText}${warning}`;
}
function updateCalibrationStatus(){
  ui.calStatus.textContent = calibrationSummary();
}
function calibrationRequiredNotice(){
  if(openMetrics && closeMetrics) return '환자별 손가락 동작 보정 기준을 사용합니다.';
  return '현재는 자동 손동작 기준을 사용합니다. 환자별 손 상태를 더 잘 반영하려면 손가락 동작 보정을 사용할 수 있습니다.';
}

function calibrationScheduleGuard(id){ return id===calStepId && combinedCalActive && running && cameraOnlyReady; }
function startFingerCalibration(){
  resetSessionForNewAction('손가락 동작 보정');
  if(!running || !cameraOnlyReady){
    setInstruction('카메라를 먼저 켜세요','① 카메라만 켜기 버튼을 누른 뒤 손가락 동작 보정을 진행합니다.','warn');
    speakText('cal_need_camera', '먼저 카메라만 켜기 버튼을 누른 뒤 손가락 동작 보정을 진행하세요.', true);
    return;
  }
  trainingActive=false; trainingPreviewActive=false; paused=false; target=null; particles=[]; stage='calibration_instruction'; holdStart=null; resetBubbleOpenGate(); clearCalibrationTimers();
  combinedCalActive=true; calMode=null; calSamples=[]; calStepId++; calWaitingForStart=true; state='cal_open_instruction'; setCalOverlayLabel('손 펴기 준비'); resetCalProgress(); updateUI();
  const id=calStepId;
  const explain = '손가락 동작 보정을 시작합니다. 먼저 손가락을 편 상태를 측정합니다. 아직 측정하지 않습니다. 이제 시작하세요 안내가 끝난 뒤 진행 바가 올라갈 때부터 측정합니다.';
  setInstruction('손가락 동작 보정: 손 펴기 설명 중','아직 측정하지 않습니다. 음성 안내가 끝난 뒤 진행 바가 올라갈 때부터 실제 측정합니다.','warn');
  speakTextWithCallback('finger_cal_open_explain_'+id, explain, true, ()=>{
    if(!calibrationScheduleGuard(id)) return;
    beginCalibrationPrepare('open', id);
  });
}
function beginCalibrationPrepare(mode, id){
  clearCalibrationTimers();
  if(!calibrationScheduleGuard(id)) return;
  calMode=null; calSamples=[]; calWaitingForStart=true; calPrepMode=mode; stage='calibration_prepare'; state=mode==='open'?'cal_open_prepare':'cal_close_prepare'; resetCalProgress();
  const modeName = mode==='open' ? '손 펴기' : '손 쥐기';
  const action = mode==='open' ? '손가락을 최대한 편 상태' : '손가락을 최대한 구부려 쥔 상태';
  setInstruction(`손가락 동작 보정: ${modeName} 준비`, '아직 측정하지 않습니다. 음성 안내가 끝난 뒤 진행 바가 올라가면 측정됩니다.', 'warn');
  const nowText = `이제 시작하세요. ${action}로 준비하세요. 진행 바가 올라가면 3초 동안 그대로 유지하세요.`;
  speakTextWithCallback('finger_cal_'+mode+'_now_'+id, nowText, true, ()=>{
    if(!calibrationScheduleGuard(id)) return;
    startCalibrationVisualCountdown(mode, id);
  }, false);
}
function startCalibrationVisualCountdown(mode, id){
  clearCalibrationTimers();
  if(!calibrationScheduleGuard(id)) return;
  const modeName = mode==='open' ? '손 펴기' : '손 쥐기';
  calPrepEnd = now() + 1200;
  setInstruction(`손가락 동작 보정: ${modeName} 측정 직전`, '이제 곧 진행 바가 올라갑니다. 아직 측정하지 않습니다.', 'warn');
  calPrepTimer=setInterval(()=>{
    if(!calibrationScheduleGuard(id)){ clearCalibrationTimers(); return; }
    const remain=Math.max(0, (calPrepEnd-now())/1000);
    resetCalProgress();
    setInstruction(`손가락 동작 보정: ${modeName} 측정 직전`, `측정 시작까지 ${remain.toFixed(1)}초. 진행 바가 올라가기 전까지는 측정하지 않습니다.`, 'warn');
    if(remain<=0){ clearCalibrationTimers(); beginCalibrationMeasurement(mode, id); }
  }, 120);
}
function beginCalibrationMeasurement(mode, id=calStepId){
  if(!calibrationScheduleGuard(id)) return;
  calMode=mode; calSamples=[]; calStart=now(); calVoiceMilestone=-1; calWaitingForStart=false; clearCalibrationTimers(); setCalOverlayLabel(mode==='open'?'손 펴기':'손 쥐기'); resetCalProgress();
  state=mode==='open'?'cal_open_count':'cal_close_count';
  stage='calibration_measure';
  const title = mode==='open' ? '손 펴기 측정 중' : '손 쥐기 측정 중';
  const sub = mode==='open' ? '지금부터 실제 측정 중입니다. 손가락을 최대한 편 상태로 유지하세요.' : '지금부터 실제 측정 중입니다. 손가락을 최대한 구부려 쥔 상태로 유지하세요.';
  setInstruction(`손가락 동작 보정: ${title}`, `${sub} 진행 바가 100%가 되면 인식됩니다.`, 'warn');
}
function beginCloseCalibrationInstruction(){
  clearCalibrationTimers();
  calMode=null; calSamples=[]; calStepId++; calWaitingForStart=true; state='cal_close_instruction'; stage='calibration_instruction'; setCalOverlayLabel('손 쥐기 준비'); resetCalProgress();
  const id=calStepId;
  const explain = '이번에는 손가락을 구부려 쥔 상태를 측정합니다. 아직 측정하지 않습니다. 이제 시작하세요 안내가 끝난 뒤 진행 바가 올라갈 때부터 측정합니다.';
  setInstruction('손가락 동작 보정: 손 쥐기 설명 중','아직 측정하지 않습니다. 음성 안내가 끝난 뒤 진행 바가 올라갈 때부터 실제 측정합니다.','warn');
  speakTextWithCallback('finger_cal_close_explain_'+id, explain, true, ()=>{
    if(!calibrationScheduleGuard(id)) return;
    beginCalibrationPrepare('close', id);
  });
}

function chooseHand(result){
  if(!result||!result.landmarks||result.landmarks.length===0) return null;
  let best=null;
  for(let i=0;i<result.landmarks.length;i++){
    const handed = result.handednesses?.[i]?.[0]?.categoryName || 'Unknown';
    const score = result.handednesses?.[i]?.[0]?.score || 0;
    if(CONFIG.affectedHand!=='Any' && handed!==CONFIG.affectedHand) continue;
    if(score<CONFIG.minHandConfidence) continue;
    if(!best || score>best.score) best={landmarks:result.landmarks[i], handed, score};
  }
  if(!best && CONFIG.affectedHand!=='Any' && result.landmarks.length>0){ return {wrongHand:true, landmarks:result.landmarks[0], handed:result.handednesses?.[0]?.[0]?.categoryName || 'Unknown', score:result.handednesses?.[0]?.[0]?.score||0}; }
  return best;
}
function smoothLm(lm){
  if(!smoothLandmarks || smoothLandmarks.length!==lm.length) smoothLandmarks = lm.map(p=>({x:p.x,y:p.y,z:p.z||0}));
  const alpha = clamp(0.18 + (1-CONFIG.robustness)*0.42, 0.15, 0.6);
  smoothLandmarks = lm.map((p,i)=>({ x:lerp(smoothLandmarks[i].x,p.x,alpha), y:lerp(smoothLandmarks[i].y,p.y,alpha), z:lerp(smoothLandmarks[i].z,p.z||0,alpha) }));
  return smoothLandmarks;
}
function handMetrics(lmRaw){
  const lm=smoothLm(lmRaw);
  const wrist=lm[0], thumb=lm[4], index=lm[8], middle=lm[12], ring=lm[16], pinky=lm[20], middleMcp=lm[9];
  const palmSize=Math.max(dist(wrist,middleMcp),0.035);
  const pinch=dist(thumb,index)/palmSize;
  const fingertipAvg=(dist(index,wrist)+dist(middle,wrist)+dist(ring,wrist)+dist(pinky,wrist))/4/palmSize;
  const palm={x:(lm[0].x+lm[5].x+lm[9].x+lm[13].x+lm[17].x)/5,y:(lm[0].y+lm[5].y+lm[9].y+lm[13].y+lm[17].y)/5};
  const cursor = CONFIG.exercise.gesture==='pinch' ? index : palm;
  const angle = Math.atan2((lm[9].y-lm[0].y),(lm[9].x-lm[0].x))*180/Math.PI;
  const spread = dist(index,pinky)/palmSize;
  return {lm, wrist, thumb, index, middle, ring, pinky, palm, cursor, palmSize, pinch, fingertipAvg, angle, spread};
}
function calibratedFingerRange(){
  const hasCal = !!(openMetrics && closeMetrics);
  let openVal = hasCal ? openMetrics.fingertipAvg : 1.75;
  let closeVal = hasCal ? closeMetrics.fingertipAvg : 1.05;
  // Fingertip distance is normally larger when the hand is open and smaller when it is grasped.
  // If calibration is inverted, use safe automatic defaults so the task remains trainable.
  if(!Number.isFinite(openVal) || !Number.isFinite(closeVal) || openVal <= closeVal){
    openVal = 1.75; closeVal = 1.05;
  }
  const diff = openVal - closeVal;
  const range = Math.max(0.08, diff);
  return {openVal, closeVal, range, calibrated:hasCal && diff>0};
}
function gestureScore(m, gesture=CONFIG.exercise.gesture){
  if(gesture==='open'){
    const r=calibratedFingerRange();
    return clamp((m.fingertipAvg-r.closeVal)/r.range,0,1);
  }
  if(gesture==='pinch'){
    const openVal=openMetrics?.pinch ?? .75;
    const closeVal=closeMetrics?.pinch ?? .18;
    const range=Math.max(.08, openVal-closeVal);
    return clamp((openVal-m.pinch)/range,0,1);
  }
  const r=calibratedFingerRange();
  return clamp((r.openVal-m.fingertipAvg)/r.range,0,1);
}
function updateGestureDisplay(m){
  smoothedGesture=lerp(smoothedGesture, gestureScore(m), .22);
  ui.gesture.textContent=`${Math.round(smoothedGesture*100)}%`;
}
function canvasPoint(p){ return {x:(CONFIG.mirrorView ? 1-p.x : p.x)*canvas.width, y:p.y*canvas.height}; }
function cursorPx(m){ const p=canvasPoint(m.cursor); if(!smoothedCursor) smoothedCursor=p; smoothedCursor={x:lerp(smoothedCursor.x,p.x,.30), y:lerp(smoothedCursor.y,p.y,.30)}; return smoothedCursor; }
function targetRadius(){ return CONFIG.levelConfig.targetRadius*CONFIG.targetSizeScale; }
function mouthRadius(base){ return Math.max(18, base*(Number(CONFIG.mouthTargetScale)||1)); }
function cupHomePosition(r){
  const mode = CONFIG.cupPositionMode || 'auto_by_hand';
  const preset = CONFIG.cupPositionPreset || 'right_lower';
  const tableY = canvas.height * (Number(CONFIG.tableHeight)||0.92);
  const tableH = canvas.height*0.16;
  const tableTop = tableY - tableH*0.28;
  const cupR = r*0.76;
  const yy = clamp(tableTop - cupR*0.02, canvas.height*0.66, canvas.height*0.88);
  let xRatio = 0.72;
  if(mode==='manual'){
    if(preset==='left_lower') xRatio = 0.24;
    else if(preset==='center_lower') xRatio = 0.50;
    else xRatio = 0.76;
  }else{
    const hand = CONFIG.affectedHand || 'Any';
    const isLeft = hand==='Left';
    const isRight = hand==='Right';
    const fallbackLeft = CONFIG.mirrorView ? 0.27 : 0.24;
    const fallbackRight = CONFIG.mirrorView ? 0.73 : 0.76;
    xRatio = isLeft ? fallbackLeft : (isRight ? fallbackRight : 0.72);
  }
  return {x:canvas.width*xRatio, y:yy, r:cupR, tableY};
}
function randomTarget(r){ const margin=r+28; return {x:margin+Math.random()*Math.max(20,canvas.width-margin*2), y:margin+Math.random()*Math.max(20,canvas.height-margin*2), r, vx:(Math.random()*2-1)*CONFIG.levelConfig.speed*CONFIG.speedScale, vy:(Math.random()*2-1)*CONFIG.levelConfig.speed*CONFIG.speedScale}; }
function mouthFallback(r){ const rr = mouthRadius(r*.78); return {x:canvas.width*.74,y:canvas.height*.25,r:rr,actual:false}; }
function spawnTaskTarget(){
  const r=targetRadius(); const type=CONFIG.exercise.taskType;
  holdStart=null; overlapStart=null; reactionStart=now(); successLock=false; targetSerial++; lastStepId=''; stepStartedAt=now();
  if(type==='bubble'){ target=randomTarget(r); target.kind='bubble'; stage='seek'; state='seek_target'; }
  else if(type==='cup_drink'){ const home=cupHomePosition(r); target={cup:{x:home.x,y:home.y,r:home.r,attached:false,filled:true,homeX:home.x,homeY:home.y,returnReady:false}, mouth:mouthFallback(r), table:{y:home.tableY}}; stage='cup_reach'; state='cup_reach'; }
  else if(type==='hand_bubbles'){ resetBubbleOpenGate(); target={kind:'air_bubbles', bubbles:[], initialized:false, lastPop:null, activeId:null, anchor:{x:canvas.width*.50,y:canvas.height*.34}, r:r*.52}; stage='air_seek'; state='air_bubble_seek'; }
  else { target=randomTarget(r); target.kind='bubble'; stage='seek'; state='seek_target'; }
}
function moveTarget(t){ if(!t||!t.vx) return; t.x+=t.vx; t.y+=t.vy; if(t.x<t.r||t.x>canvas.width-t.r) t.vx*=-1; if(t.y<t.r||t.y>canvas.height-t.r) t.vy*=-1; }
function insidePoint(p,obj,scale=1.0){ return Math.hypot(p.x-obj.x,p.y-obj.y) <= obj.r*scale; }
function holdProgress(){ return holdStart ? (now()-holdStart)/CONFIG.holdMs : 0; }
function beginHold(){ if(!holdStart){ holdStart=now(); speakOnce('hold_gesture'); } }
function resetHold(){ holdStart=null; }
function resetCurrentAttempt(){
  holdStart=null; overlapStart=null; reactionStart=now(); neutralTilt=null; successLock=false; resetBubbleOpenGate();
  if(CONFIG.exercise.taskType==='hand_bubbles' && target && target.kind==='air_bubbles'){
    target.activeId = null; stage='air_seek'; state='air_bubble_seek';
  }else{
    spawnTaskTarget();
  }
}
function taskProgressItem(){
  if(CONFIG.exercise.taskType==='hand_bubbles') return '공기방울';
  if(CONFIG.exercise.taskType==='cup_drink') return '과제';
  return CONFIG.exerciseKey==='bubble_pinch' ? '작은 물방울' : '물방울';
}
function remainProgressText(remain){
  return CONFIG.exercise.taskType==='cup_drink' ? `남은 반복은 ${remain}회입니다.` : `남은 ${taskProgressItem()}은 ${remain}개입니다.`;
}
function successProgressText(count){
  return CONFIG.exercise.taskType==='cup_drink' ? `현재까지 ${count}회 성공했습니다.` : `${taskProgressItem()} ${count}개를 완료했습니다.`;
}
function onFailure(reason='잘못 수행되었습니다.'){
  if(state==='complete' || now()-lastFailureAt<4500) return;
  lastFailureAt=now(); attempts++; failureCount++;
  const remain = CONFIG.exercise.taskType==='hand_bubbles' ? remainingBubbles() : Math.max(0, CONFIG.targetCount-score);
  setInstruction('다시 시도하세요', `${reason} 성공으로 기록하지 않습니다. 남은 목표를 다시 수행하세요.`, 'bad');
  speakText('fail_'+targetSerial, `${reason} 이번 시도는 성공으로 기록하지 않습니다. 준비 자세로 돌아온 뒤 다시 수행하세요. ${remainProgressText(remain)}`, true);
  resetCurrentAttempt();
  updateUI();
}
function checkStepTimeout(){
  const id = stage + '|' + state;
  if(id!==lastStepId){ lastStepId=id; stepStartedAt=now(); }
  const active = ['do_gesture','hold_gesture','cup_reach','cup_to_mouth','cup_return','air_bubble_seek','air_bubble_grasp','air_bubble_hold'];
  const isActive = active.includes(state) || ['cup_reach','cup_to_mouth','cup_return','air_seek','air_hold'].includes(stage);
  if(isActive && now()-stepStartedAt > CONFIG.stepTimeoutMs){
    onFailure('현재 단계가 오래 지속되었습니다.');
  }
}
function onSuccess(){
  if(successLock || state==='complete') return;
  successLock=true; holdStart=null; stage='success_pause'; state='success_pause';
  score++; successes++; attempts++; const rtSec = reactionStart ? (now()-reactionStart)/1000 : 0; if(reactionStart) reactionTimes.push(rtSec); successTimes.push(rtSec); addParticles(); updateUI();
  const remain = CONFIG.targetCount - score;
  if(score>=CONFIG.targetCount || (CONFIG.exercise.taskType==='hand_bubbles' && remainingBubbles()<=0)){ completeGame(); return; }
  setInstruction('정상적으로 성공했습니다', `${successProgressText(score)} ${remainProgressText(remain)}`, 'ready');
  speakStagePrompt('rep_success_'+score, `성공했습니다. ${remainProgressText(remain)}`, true);
  const thisRun=trainingRunId;
  setTimeout(()=>{ if(thisRun===trainingRunId && trainingActive && running&&!paused&&state!=='complete'){
    if(CONFIG.exercise.taskType==='hand_bubbles' && target && target.kind==='air_bubbles'){ holdStart=null; successLock=false; resetBubbleOpenGate(); stage='air_seek'; state='air_bubble_seek'; reactionStart=now(); target.activeId=null; }
    else{ spawnTaskTarget(); speakTextNoScreen('rep_start_'+targetSerial, taskStartText(), true); }
  } }, 1500);
}
function addParticles(){ const pop=target?.lastPop || target; const px=(pop?.x||target?.x||target?.cup?.x||canvas.width/2), py=(pop?.y||target?.y||target?.cup?.y||canvas.height/2); for(let i=0;i<24;i++){ particles.push({x:px, y:py, vx:(Math.random()*2-1)*3.4, vy:(Math.random()*2-1)*3.4, life:32+Math.random()*24}); } }

function processBubble(m){
  if(!target) spawnTaskTarget(); moveTarget(target);
  const c=cursorPx(m); const inside=insidePoint(c,target,1.05); const g=smoothedGesture>=CONFIG.gestureThreshold;
  if(!inside){ resetHold(); if(now()-lastStatusVoice>4500){speakStagePrompt('seek_target_'+targetSerial,'목표 위치로 손을 가져가세요.', false); lastStatusVoice=now();} setInstruction(`1단계: ${CONFIG.exercise.targetName}에 손을 가져가세요`,'목표 안에 손이 들어가면 다음 단계 안내가 나옵니다.','info'); state='seek_target'; return; }
  if(!g){ resetHold(); const action=CONFIG.exercise.gesture==='pinch'?'엄지와 검지를 맞대세요':CONFIG.exercise.gesture==='open'?'손을 충분히 펴세요':'손을 쥐세요'; speakStagePrompt('now_gesture_'+targetSerial, action, false); setInstruction(`2단계: ${action}`,'목표 안에서 끝동작을 수행하고 잠시 유지합니다.','action'); state='do_gesture'; return; }
  if(!holdStart){ holdStart=now(); speakStagePrompt('hold_gesture_'+targetSerial,'그대로 유지하세요.', true); } const hp=holdProgress(); setInstruction('3단계: 끝동작을 잠시 유지하세요',`${Math.round(clamp(hp,0,1)*100)}%`, 'warn'); state='hold_gesture'; if(hp>=1) onSuccess();
}

function bubbleSpeedPx(){
  const s=Number(CONFIG.speedScale)||0;
  if(s<=0.01) return 0;
  const base = 0.42 + (CONFIG.levelConfig.speed||0)*0.72 + CONFIG.level*0.045;
  return clamp(base * Math.pow(s, 1.32) * 1.35, 0, 7.2);
}
function makeAirBubble(id,x,y,r){
  const angle=Math.random()*Math.PI*2;
  const speed=bubbleSpeedPx()*(0.72+Math.random()*0.56);
  return {id,x,y,r,baseX:x,baseY:y,vx:Math.cos(angle)*speed,vy:Math.sin(angle)*speed,popped:false,locked:false, shimmer:Math.random()*Math.PI*2};
}
function bubbleAnchor(){
  const mouthRef = (target?.mouth && target.mouth.actual!==false) ? target.mouth : smoothedMouth;
  if(CONFIG.trackMouth && mouthRef){
    return {x: mouthRef.x, y: clamp(mouthRef.y + targetRadius()*1.9, canvas.height*0.28, canvas.height*0.72)};
  }
  return {x: canvas.width*0.5, y: canvas.height*0.36};
}
function bubbleLayoutBounds(anchor, r, count){
  const cols = Math.max(2, Math.ceil(Math.sqrt(count * canvas.width / Math.max(1, canvas.height*0.56))));
  const rows = Math.ceil(count/cols);
  const areaW = canvas.width*0.88;
  const areaH = canvas.height*0.58;
  const safeR = Math.max(16, Math.min(r, areaW/(cols*3.35), areaH/(rows*3.35)));
  const left = clamp(anchor.x-areaW/2, safeR+22, canvas.width-safeR-22);
  const right = clamp(anchor.x+areaW/2, safeR+22, canvas.width-safeR-22);
  const top = clamp(anchor.y-safeR*.25, safeR+22, canvas.height-safeR-22);
  const bottom = clamp(anchor.y+areaH, safeR+22, canvas.height-safeR-22);
  return {cols, rows, r:safeR, left, right, top, bottom, areaW:right-left, areaH:bottom-top};
}
function buildBubbleCluster(){
  if(!target || target.kind!=='air_bubbles') return;
  const anchor = bubbleAnchor();
  target.anchor = anchor;
  const count = CONFIG.targetCount;
  const layout = bubbleLayoutBounds(anchor, target.r || targetRadius()*0.52, count);
  const baseR = layout.r;
  target.bubbles = [];
  for(let i=0;i<count;i++){
    const col=i%layout.cols, row=Math.floor(i/layout.cols);
    const cellW = layout.cols<=1 ? 0 : layout.areaW/(layout.cols-1);
    const cellH = layout.rows<=1 ? 0 : layout.areaH/(layout.rows-1);
    const jitterX = (Math.random()*2-1)*baseR*0.18;
    const jitterY = (Math.random()*2-1)*baseR*0.18;
    const x = layout.cols===1 ? anchor.x : clamp(layout.left + col*cellW + jitterX, baseR+18, canvas.width-baseR-18);
    const y = layout.rows===1 ? anchor.y : clamp(layout.top + row*cellH + jitterY, baseR+18, canvas.height-baseR-18);
    const rr = baseR*(0.92 + Math.random()*0.10);
    target.bubbles.push(makeAirBubble(`${targetSerial}_${i}_${Math.random()}`, x, y, rr));
  }
  for(let pass=0; pass<18; pass++) separateBubbles(true);
  target.initialized = true;
}
function ensureAirBubbles(){
  if(!target || target.kind!=='air_bubbles') return;
  if(!target.initialized || !target.bubbles || target.bubbles.length===0){
    buildBubbleCluster();
  }
}
function separateBubbles(strong=false){
  if(!target?.bubbles) return;
  const list=target.bubbles.filter(b=>!b.popped);
  for(let i=0;i<list.length;i++){
    for(let j=i+1;j<list.length;j++){
      const a=list[i], b=list[j];
      let dx=b.x-a.x, dy=b.y-a.y;
      let d=Math.hypot(dx,dy);
      if(d<0.001){ dx=(Math.random()*2-1); dy=(Math.random()*2-1); d=Math.hypot(dx,dy); }
      const minD=(a.r+b.r)*1.62 + 12;
      if(d<minD){
        const push=(minD-d)/(strong?1.15:1.55);
        const nx=dx/d, ny=dy/d;
        a.x-=nx*push; a.y-=ny*push; b.x+=nx*push; b.y+=ny*push;
        a.baseX=a.x; a.baseY=a.y; b.baseX=b.x; b.baseY=b.y;
        const avx=a.vx, avy=a.vy;
        a.vx=-b.vx*0.75 || -nx*0.35; a.vy=-b.vy*0.75 || -ny*0.35;
        b.vx=-avx*0.75 || nx*0.35; b.vy=-avy*0.75 || ny*0.35;
      }
    }
  }
  const anchor=target.anchor || bubbleAnchor();
  const layout=bubbleLayoutBounds(anchor, target.r || targetRadius()*0.52, CONFIG.targetCount);
  for(const b of list){
    b.x=clamp(b.x,b.r+18,canvas.width-b.r-18); b.y=clamp(b.y,b.r+18,canvas.height-b.r-18);
    b.baseX=clamp(b.baseX,layout.left-b.r,layout.right+b.r); b.baseY=clamp(b.baseY,layout.top-b.r,layout.bottom+b.r);
  }
}
function moveAirBubbles(){
  if(!target?.bubbles) return;
  const anchor = bubbleAnchor();
  target.anchor = anchor;
  const layout=bubbleLayoutBounds(anchor, target.r || targetRadius()*0.52, CONFIG.targetCount);
  const moving = (Number(CONFIG.speedScale)||0) > 0.01;
  for(const b of target.bubbles){
    if(b.popped) continue;
    b.shimmer += 0.04 + 0.012*(Number(CONFIG.speedScale)||0);
    if(moving){
      b.x += b.vx;
      b.y += b.vy;
      if(b.x < layout.left || b.x > layout.right){ b.vx *= -1; b.x=clamp(b.x,layout.left,layout.right); }
      if(b.y < layout.top || b.y > layout.bottom){ b.vy *= -1; b.y=clamp(b.y,layout.top,layout.bottom); }
      b.baseX = b.x; b.baseY = b.y;
    }
  }
  for(let pass=0; pass<3; pass++) separateBubbles(false);
}
function nearestAirBubble(c){
  let best=null, bestD=Infinity;
  for(const b of target?.bubbles||[]){
    if(b.popped) continue;
    const d=Math.hypot(c.x-b.x,c.y-b.y);
    if(d < b.r*1.08 && d < bestD){best=b; bestD=d;}
  }
  return best;
}
function remainingBubbles(){
  return (target?.bubbles||[]).filter(b=>!b.popped).length;
}
function openGestureThreshold(){ return clamp(CONFIG.gestureThreshold*0.38, 0.08, 0.30); }
function openReadyThreshold(){ return clamp(0.52 - (CONFIG.level-1)*0.025, 0.40, 0.55); }
function graspReadyThreshold(){ return clamp(CONFIG.gestureThreshold*0.95, 0.16, 0.86); }
function rawCloseScore(m){ return gestureScore(m, 'grasp'); }
function rawOpenScore(m){ return gestureScore(m, 'open'); }
function openMaxCloseScore(){ return clamp(graspReadyThreshold()*0.58, 0.12, 0.38); }
function graspMaxOpenScore(){ return 0.54; }
function isHandOpenEnough(m){ return rawOpenScore(m) >= openReadyThreshold() && rawCloseScore(m) <= openMaxCloseScore(); }
function isHandGraspEnough(m){ return rawCloseScore(m) >= graspReadyThreshold() && rawOpenScore(m) <= graspMaxOpenScore(); }
function isCupGripEnough(m){ return isHandGraspEnough(m); }
function resetBubbleOpenGate(){ bubbleOpenReady=false; bubbleOpenStart=0; bubbleCandidateId=null; }
function registerOpenHand(m, minMs=700){
  if(isHandOpenEnough(m)){
    if(!bubbleOpenStart) bubbleOpenStart=now();
    if(now()-bubbleOpenStart>=minMs) bubbleOpenReady=true;
  }else{
    bubbleOpenStart=0; bubbleOpenReady=false;
  }
  return bubbleOpenReady;
}
function processHandBubbles(m){
  if(!trainingActive) return;
  if(!target || target.kind!=='air_bubbles') spawnTaskTarget();
  ensureAirBubbles();
  moveAirBubbles();
  const c=cursorPx(m);
  const b=nearestAirBubble(c);
  const currentId=b ? b.id : null;
  if(currentId!==bubbleCandidateId){
    bubbleCandidateId=currentId;
    holdStart=null;
    bubbleOpenStart=0;
    bubbleOpenReady=false;
  }
  target.activeId = currentId;
  const closeScore=rawCloseScore(m);
  const openScore=rawOpenScore(m);
  const openOK=isHandOpenEnough(m);
  const graspOK=isHandGraspEnough(m);
  const remain = remainingBubbles();
  if(remain<=0){ completeGame(); return; }
  if(!b){
    holdStart=null;
    bubbleOpenStart=0;
    bubbleOpenReady=false;
    if(now()-lastStatusVoice>5200){
      speakStagePrompt('stage_bubble_seek_'+score, `방울 하나로 손을 가져가세요.`, false);
      lastStatusVoice=now();
    }
    setInstruction('1단계: 물방울 하나에 손을 가져가세요', `남은 물방울 ${remain}개. 먼저 손 편 상태가 확인되어야 성공 단계로 넘어갑니다. 손 편 점수 ${Math.round(openScore*100)}%, 손쥐기 점수 ${Math.round(closeScore*100)}%.`, 'info');
    stage='air_seek'; state='air_bubble_seek'; return;
  }
  if(!bubbleOpenReady){
    if(openOK){
      if(!bubbleOpenStart) bubbleOpenStart=now();
      const openPct = clamp((now()-bubbleOpenStart)/900,0,1);
      setInstruction('2단계: 같은 물방울 안에서 먼저 손을 펴세요', `손 편 상태 확인 ${Math.round(openPct*100)}%. 손 편 점수 ${Math.round(openScore*100)}% / 기준 ${Math.round(openReadyThreshold()*100)}%, 손쥐기 점수 ${Math.round(closeScore*100)}% / 허용 ${Math.round(openMaxCloseScore()*100)}%.`, 'warn');
      stage='air_open_required'; state='air_bubble_open_required';
      if(openPct<1) return;
      bubbleOpenReady=true;
      holdStart=null;
      speakStagePrompt('stage_open_confirmed_'+score, '손 펴기 확인. 이제 같은 방울 안에서 손을 쥐세요.', true);
    }else{
      bubbleOpenStart=0; holdStart=null;
      if(now()-lastStatusVoice>4200){ speakStagePrompt('stage_need_open_'+score, '먼저 손가락을 펴세요.', false); lastStatusVoice=now(); }
      setInstruction('먼저 손가락을 충분히 펴세요', `손 편 상태가 먼저 확인되어야 합니다. 손 편 점수 ${Math.round(openScore*100)}% / 기준 ${Math.round(openReadyThreshold()*100)}%, 손쥐기 점수 ${Math.round(closeScore*100)}% / 허용 ${Math.round(openMaxCloseScore()*100)}%.`, 'warn');
      stage='air_open_required'; state='air_bubble_open_required'; return;
    }
  }
  if(!graspOK){
    holdStart=null;
    if(now()-lastStatusVoice>4200){ speakStagePrompt('stage_bubble_grasp_'+score, '이제 손을 쥐세요.', false); lastStatusVoice=now(); }
    setInstruction('3단계: 손가락을 굽혀 쥐세요', `손쥐기 점수 ${Math.round(closeScore*100)}% / 기준 ${Math.round(graspReadyThreshold()*100)}%, 손 편 점수 ${Math.round(openScore*100)}% / 허용 ${Math.round(graspMaxOpenScore()*100)}%.`, 'action');
    stage='air_grasp'; state='air_bubble_grasp'; return;
  }
  if(!holdStart){ holdStart=now(); speakStagePrompt('stage_bubble_hold_'+score, '그대로 유지하세요.', true); }
  const hp=holdProgress();
  setInstruction('4단계: 잡은 상태를 잠시 유지하세요', `유지 ${Math.round(clamp(hp,0,1)*100)}% · 남은 물방울 ${remain}개`, 'warn');
  stage='air_hold'; state='air_bubble_hold';
  if(hp>=1 && !b.popped && !b.locked){
    b.locked = true;
    b.popped = true;
    target.lastPop={x:b.x,y:b.y,r:b.r};
    resetBubbleOpenGate();
    onSuccess();
  }
}

function updateMouthTargetFromFace(faceResult){
  if(!CONFIG.trackMouth) return;
  let detected=null;
  try{
    const faces=faceResult?.faceLandmarks || [];
    if(faces.length>0){
      const lm=faces[0];
      const pts=[13,14,61,291].map(i=>lm[i]).filter(Boolean);
      if(pts.length>=2){
        const avg=pts.reduce((a,p)=>({x:a.x+p.x,y:a.y+p.y}),{x:0,y:0});
        let x=avg.x/pts.length, y=avg.y/pts.length;
        const left=lm[61], right=lm[291];
        let mouthWidth=0;
        if(left&&right) mouthWidth=Math.hypot((left.x-right.x)*canvas.width,(left.y-right.y)*canvas.height);
        const px={x:(CONFIG.mirrorView?1-x:x)*canvas.width, y:y*canvas.height};
        const baseR=mouthRadius(targetRadius()*0.50);
        const r=clamp(Math.max(baseR, mouthWidth*1.20*(Number(CONFIG.mouthTargetScale)||1)), mouthRadius(targetRadius()*0.42), mouthRadius(targetRadius()*0.90));
        detected={x:px.x,y:px.y,r,actual:true};
      }
    }
  }catch(e){ detected=null; }
  if(detected){
    mouthDetectedAt=now();
    if(!smoothedMouth) smoothedMouth=detected;
    smoothedMouth={x:lerp(smoothedMouth.x,detected.x,.35),y:lerp(smoothedMouth.y,detected.y,.35),r:lerp(smoothedMouth.r,detected.r,.25),actual:true};
    if(target?.mouth){ target.mouth={...smoothedMouth}; }
  }else if(now()-mouthDetectedAt>900){
    if(stage==='cup_to_mouth' && now()-lastMouthVoice>4500){ speakOnce('mouth_not_found'); lastMouthVoice=now(); }
    if(target?.mouth) target.mouth.actual=false;
  }
}
function mouthReady(){
  if(!CONFIG.trackMouth) return true;
  return !!(target?.mouth?.actual) || (now()-mouthDetectedAt<1200);
}
function processCupDrink(m){
  const c=cursorPx(m); const cup=target.cup, mouth=target.mouth;
  const closeScore=rawCloseScore(m);
  const openScore=rawOpenScore(m);
  const gripOK=isCupGripEnough(m);
  const home = {x:cup.homeX, y:cup.homeY, r:cup.r*1.10};
  function releaseCup(reason='손이 펴져 컵을 놓았습니다.'){
    cup.attached=false; cup.x=cup.homeX; cup.y=cup.homeY; holdStart=null; stage='cup_reach'; state='cup_reach';
    speakStagePrompt('cup_released_'+targetSerial, '컵을 놓았습니다. 다시 쥐어 주세요.', true);
    setInstruction('컵을 놓았습니다', `${reason} 물컵은 원래 위치로 돌아갑니다.`, 'warn');
  }
  if(stage==='cup_reach'){
    cup.attached=false; cup.x=cup.homeX; cup.y=cup.homeY;
    if(!insidePoint(c,home,1.02)){
      resetHold();
      if(now()-lastStatusVoice>4800){ speakStagePrompt('cup_reach_'+targetSerial, '탁자 위 컵으로 손을 가져가세요.', false); lastStatusVoice=now(); }
      setInstruction('1단계: 탁자 위 물컵으로 손을 가져가세요','화면 하단 탁자 위 물컵 안으로 손바닥 중심을 천천히 이동합니다.','info');
      return;
    }
    if(!gripOK){
      resetHold();
      if(now()-lastStatusVoice>3600){ speakStagePrompt('cup_grasp_'+targetSerial, '컵 안에서 손을 쥐세요.', false); lastStatusVoice=now(); }
      setInstruction('2단계: 물컵을 손으로 쥐어 잡으세요',`손을 편 상태에서는 컵이 움직이지 않습니다. 손쥐기 점수 ${Math.round(closeScore*100)}% / 기준 ${Math.round(graspReadyThreshold()*100)}%.`, 'action');
      return;
    }
    if(!holdStart){ holdStart=now(); speakStagePrompt('cup_grasp_hold_'+targetSerial, '컵을 쥔 상태로 잠시 유지하세요.', true); }
    setInstruction('물컵을 쥔 상태를 유지하세요',`${Math.round(clamp(holdProgress(),0,1)*100)}%`, 'warn');
    if(holdProgress()>=1){
      cup.attached=true; stage='cup_to_mouth'; state='cup_to_mouth'; resetHold(); lastStatusVoice=0;
      speakStagePrompt('stage_cup_to_mouth_'+targetSerial, '잡았습니다. 입 위치로 옮기세요.', true);
    }
    return;
  }
  if(stage==='cup_to_mouth'){
    if(!gripOK){ releaseCup('손쥐기 동작이 풀렸습니다.'); return; }
    cup.attached=true; cup.x=c.x; cup.y=c.y;
    if(!mouthReady()){
      resetHold();
      if(now()-lastStatusVoice>4200){ speakStagePrompt('mouth_not_found_'+targetSerial, '입 위치가 보이도록 얼굴을 보여 주세요.', false); lastStatusVoice=now(); }
      setInstruction('입 위치가 보이도록 얼굴을 보여 주세요','얼굴과 입 주변이 화면에 보이면 실제 입 위치 목표가 표시됩니다.','warn');
      return;
    }
    if(!insidePoint(c,mouth,.95)){
      resetHold();
      if(now()-lastStatusVoice>5200){ speakStagePrompt('cup_to_mouth_'+targetSerial, '컵을 입 위치로 옮기세요.', false); lastStatusVoice=now(); }
      setInstruction('3단계: 컵을 쥔 상태로 실제 입 위치로 옮기세요', mouth.actual?'파란 원은 현재 화면에서 인식된 실제 입 위치입니다.':'파란 원은 입 위치 추정 목표입니다.', 'drink');
      return;
    }
    if(!holdStart){ holdStart=now(); speakStagePrompt('cup_drink_hold_'+targetSerial, '입 위치입니다. 잠시 멈추세요.', true); }
    setInstruction('입 위치에서 컵을 쥔 상태로 잠시 멈추세요',`${Math.round(clamp(holdProgress(),0,1)*100)}%`, 'warn');
    if(holdProgress()>=1){
      cup.filled=false; cup.returnReady=true; stage='cup_return'; state='cup_return'; resetHold(); lastStatusVoice=0;
      speakStagePrompt('stage_cup_return_'+targetSerial, '마셨습니다. 빈 컵을 원래 위치로 옮기세요.', true);
    }
    return;
  }
  if(stage==='cup_return'){
    if(!gripOK){ releaseCup('컵을 돌려놓기 전에 손쥐기 동작이 풀렸습니다.'); return; }
    cup.attached=true; cup.x=c.x; cup.y=c.y;
    if(!insidePoint(c,home,1.02)){
      resetHold();
      if(now()-lastStatusVoice>5200){ speakStagePrompt('cup_return_'+targetSerial, '빈 컵을 원래 위치로 옮기세요.', false); lastStatusVoice=now(); }
      setInstruction('4단계: 빈 컵을 원래 위치로 가져가세요','하단 탁자 위 밝은 받침 위치에 컵을 다시 놓아 주세요.','drink');
      return;
    }
    if(!holdStart){ holdStart=now(); speakStagePrompt('cup_home_hold_'+targetSerial, '원래 위치입니다. 잠시 유지하세요.', true); }
    setInstruction('원래 위치에 컵을 놓고 잠시 유지하세요',`${Math.round(clamp(holdProgress(),0,1)*100)}%`, 'warn');
    if(holdProgress()>=1){
      cup.attached=false; cup.x=cup.homeX; cup.y=cup.homeY; resetHold(); onSuccess();
    }
  }
}
function angleDelta(a,b){ let d=a-b; while(d>180)d-=360; while(d<-180)d+=360; return d; }
function processPourDrink(m){
  const c=cursorPx(m); const p=target.pitcher, cup=target.cup, mouth=target.mouth; const g=smoothedGesture>=CONFIG.gestureThreshold || CONFIG.level===1;
  if(stage==='pour_reach_pitcher'){
    if(!insidePoint(c,p,1.08)){ resetHold(); speakOnce('pour_reach_pitcher'); setInstruction('1단계: 물병으로 손을 가져가세요','손바닥 중심이 물병 몸통 영역에 들어가도록 이동합니다.','info'); return; }
    if(!g){ resetHold(); speakOnce('pour_grasp_pitcher'); setInstruction('2단계: 물병을 잡으세요','손을 쥐어 물병을 잡고 잠시 유지합니다.','action'); return; }
    beginHold(); setInstruction('물병을 잡은 상태를 유지하세요',`${Math.round(clamp(holdProgress(),0,1)*100)}%`, 'warn'); if(holdProgress()>=1){ p.attached=true; stage='pour_move_to_cup'; neutralTilt=m.angle; resetHold(); speakText('stage_pour_to_cup_'+targetSerial, '좋습니다. 물병을 잡은 상태로 컵 위까지 천천히 옮기세요.', true); }
    return;
  }
  if(stage==='pour_move_to_cup'){
    p.x=c.x; p.y=c.y;
    if(!insidePoint(c,cup,1.15)){ resetHold(); setInstruction('물병을 컵 위로 옮기세요','컵 위 목표 영역까지 이동합니다.','drink'); return; }
    const tilt=Math.abs(angleDelta(m.angle, neutralTilt||m.angle));
    if(tilt < CONFIG.levelConfig.tiltDeg){ resetHold(); speakOnce('pour_tilt'); setInstruction('3단계: 손목을 기울여 물을 따르세요',`기울임 ${tilt.toFixed(0)}° / 목표 ${CONFIG.levelConfig.tiltDeg}°`, 'action'); return; }
    beginHold(); setInstruction('물을 따르는 자세를 유지하세요',`${Math.round(clamp(holdProgress(),0,1)*100)}%`, 'warn'); if(holdProgress()>=1){ cup.filled=true; p.attached=false; stage='cup_reach'; resetHold(); speakText('stage_pour_done_'+targetSerial, '물이 채워졌습니다. 이제 물컵을 잡으세요.', true); }
    return;
  }
  if(stage==='cup_reach'){
    if(!insidePoint(c,cup,1.08)){ resetHold(); setInstruction('물이 담긴 컵으로 손을 가져가세요','컵을 잡기 위해 손을 컵으로 이동합니다.','info'); return; }
    if(!g){ resetHold(); speakOnce('cup_grasp'); setInstruction('물이 담긴 컵을 잡으세요','손을 쥔 상태를 유지합니다.','action'); return; }
    beginHold(); setInstruction('컵을 잡은 상태를 유지하세요',`${Math.round(clamp(holdProgress(),0,1)*100)}%`, 'warn'); if(holdProgress()>=1){ cup.attached=true; stage='cup_to_mouth'; resetHold(); speakText('stage_cup_to_mouth_'+targetSerial, '좋습니다. 이제 물컵을 실제 입 위치까지 천천히 옮기세요.', true); }
    return;
  }
  if(stage==='cup_to_mouth'){
    cup.x=c.x; cup.y=c.y;
    if(!mouthReady()){ resetHold(); setInstruction('입 위치가 보이도록 얼굴을 보여 주세요','얼굴과 입 주변이 화면에 보이면 실제 입 위치 목표가 표시됩니다.','warn'); return; }
    if(!insidePoint(c,mouth,.95)){ resetHold(); setInstruction('물컵을 실제 입 위치로 옮기세요', mouth.actual?'파란 원은 현재 화면에서 인식된 입 위치입니다.':'파란 원은 입 위치 추정 목표입니다.', 'drink'); return; }
    beginHold(); speakOnce('cup_drink_hold'); setInstruction('3단계: 입 위치에서 잠시 멈추세요',`${Math.round(clamp(holdProgress(),0,1)*100)}%`, 'warn'); if(holdProgress()>=1) onSuccess();
  }
}
function processGame(m,handed,handScore){
  if(state==='complete') return;
  ui.hand.textContent=`${handed} (${Math.round(100*handScore)}%)`;
  updateGestureDisplay(m);
  if(combinedCalActive){
    if(calMode){ processCalibration(m); }
    else if(calWaitingForStart){
      if(stage==='calibration_prepare'){
        const modeName = calPrepMode==='close' ? '손 쥐기' : '손 펴기';
        const remain = calPrepEnd ? Math.max(0,(calPrepEnd-now())/1000) : 0;
        resetCalProgress();
        setInstruction(`손가락 동작 보정: ${modeName} 측정 준비`, `측정 시작까지 ${remain.toFixed(1)}초. 아직 측정하지 않습니다.`, 'warn');
      }else{
        setInstruction(state==='cal_close_instruction'?'손 쥐기 설명 중':'손 펴기 설명 중','아직 측정하지 않습니다. 음성 안내가 끝난 뒤 준비 시간이 지나야 진행 바가 올라갑니다.','warn');
      }
    }
    return;
  }
  if(!trainingActive){
    if(trainingPreviewActive){
      setInstruction('목표 확인','', 'ready');
      return;
    }
    target=null; particles=[];
    if(stage==='training_instruction' || stage==='training_prepare'){ return; }
    if(!calMode && state!=='camera_only_ready'){
      state='camera_only_ready'; stage='camera_only_ready';
      setInstruction('카메라만 켜진 상태입니다','보정을 완료한 뒤 ④ 훈련 시작 버튼을 눌러야 선택한 훈련 과제가 나타납니다.','ready');
    }
    return;
  }
  const type=CONFIG.exercise.taskType;
  if(!target) spawnTaskTarget();
  if(type==='bubble') processBubble(m); else if(type==='cup_drink') processCupDrink(m); else if(type==='hand_bubbles') processHandBubbles(m); else processBubble(m);
  checkStepTimeout();
}
function processCalibration(m){
  if(calMode!=='open' && calMode!=='close') return;
  const elapsed=now()-calStart;
  if(elapsed < 0){
    setCalProgress(0);
    const modeName = calMode==='open' ? '손 펴기' : '손 쥐기';
    setInstruction(`손가락 동작 보정: ${modeName} 측정 준비`, '곧 측정이 시작됩니다. 화면의 진행 바가 올라갈 때부터 손 모양을 유지하세요.', 'warn');
    return;
  }
  const progress=clamp(elapsed/calDurationMs,0,1);
  setCalProgress(progress);
  calSamples.push({pinch:m.pinch,fingertipAvg:m.fingertipAvg,angle:m.angle});
  const remain=Math.max(0, calDurationMs/1000-elapsed/1000);
  const modeName = calMode==='open' ? '손 펴기' : '손 쥐기';
  setInstruction(`손가락 동작 보정: ${modeName} 측정 중`, `진행률 ${Math.round(progress*100)}% · 남은 시간 ${remain.toFixed(1)}초 · 현재 손가락 거리값 ${m.fingertipAvg.toFixed(2)}`, 'warn');
  if(progress<1) return;
  setCalProgress(1);
  const avg={pinch:mean(calSamples.map(s=>s.pinch)),fingertipAvg:mean(calSamples.map(s=>s.fingertipAvg)),angle:mean(calSamples.map(s=>s.angle))};
  const finishedMode=calMode;
  calMode=null; calSamples=[]; calVoiceMilestone=-1; calWaitingForStart=false;
  if(finishedMode==='open'){
    openMetrics=avg; updateCalibrationStatus(); playCalibrationBeepDone();
    setInstruction('손 펴기 100% 인식되었습니다', `손 편 기준 ${openMetrics.fingertipAvg.toFixed(2)} 저장 완료. 다음은 손 쥐기 보정입니다.`, 'ready');
    const openDoneId = calStepId;
    speakTextWithCallback('finger_cal_open_done_'+openDoneId, '100퍼센트. 손가락 펴기 동작이 인식되었습니다. 다음은 손가락 굽힘 동작입니다.', true, ()=>{ if(combinedCalActive && openDoneId===calStepId) beginCloseCalibrationInstruction(); });
    return;
  }
  closeMetrics=avg;
  combinedCalActive=false; calMode=null; calSamples=[]; calVoiceMilestone=-1; calWaitingForStart=false; setCalProgress(1); updateCalibrationStatus();
  const r=calibratedFingerRange();
  const warnText = (!r.calibrated || r.range<0.10) ? ' 손 펴기와 손 쥐기 차이가 작게 측정되었습니다. 그래도 자동 보정 보완 기준으로 훈련할 수 있습니다. 필요하면 다시 보정하세요.' : '';
  hideHandLandmarksUntil=now()+3200;
  playCalibrationBeepDone();
  setInstruction('손가락 동작 보정 완료', `손 편 기준 ${openMetrics.fingertipAvg.toFixed(2)} / 쥔 기준 ${closeMetrics.fingertipAvg.toFixed(2)}. 이제 ④ 훈련 시작을 누르세요.`, 'ready');
  speakText('finger_cal_done_'+calStepId, `100퍼센트. 손가락 굽힘 동작이 인식되었습니다. 손가락 동작 보정이 완료되었습니다. 이제 훈련 시작 버튼을 눌러 훈련을 시작하세요.${warnText}`, true);
  state='camera_only_ready'; stage='camera_only_ready'; trainingActive=false; trainingPreviewActive=false; target=null; particles=[];
}
function completeGame(){
  if(state==='complete') return;
  stopAllSpeech('완료 안내');
  state='complete'; stage='complete'; trainingActive=false; paused=true;
  const totalSec=(now()-gameStartTime)/1000;
  const meanRt=mean(reactionTimes);
  const failCount=failureCount;
  const unitText = CONFIG.exercise.taskType==='cup_drink' ? '회' : '개';
  const itemText = taskProgressItem();
  const completeVoice = `축하합니다. 목표 과제를 성공적으로 달성했습니다. 총 ${CONFIG.targetCount}${unitText}의 ${itemText} 과제 중 ${successes}${unitText}를 성공했습니다. 실패 횟수는 ${failCount}회이고, 평균 성공 시간은 ${meanRt.toFixed(2)}초입니다. 훈련을 종료합니다. 화면의 결과 저장 버튼을 눌러 기록을 저장할 수 있습니다.`;
  setInstruction('훈련을 성공적으로 달성했습니다',`성공 ${successes}${CONFIG.exercise.taskType==='cup_drink'?'회':'개'} · 실패 ${failCount}회 · 평균 성공시간 ${meanRt.toFixed(2)}초`, 'ready');
  speakStagePrompt('complete_summary_'+targetSerial, completeVoice, true);
  const result={date:new Date().toISOString(), exercise:CONFIG.exercise.label, hand:CONFIG.affectedHand, level:CONFIG.level, targetCount:CONFIG.targetCount, successCount:successes, failureCount:failCount, totalSeconds:Number(totalSec.toFixed(1)), meanReactionTimeSeconds:Number(meanRt.toFixed(2)), successTimes: successTimes.map(v=>Number(v.toFixed(2))), holdMs:CONFIG.holdMs, gestureThreshold:CONFIG.gestureThreshold, note:'단일 웹캠 기반 교육/피드백용 손 기능 가상훈련 결과입니다. 임상 진단용으로 사용하려면 별도 검증이 필요합니다.'};
  const text=`손 기능 재활 가상훈련 결과
측정일시: ${result.date}
훈련과제: ${result.exercise}
훈련 손: ${result.hand}
난이도: ${result.level}
목표 개수: ${result.targetCount}
성공 횟수: ${result.successCount}
실패 횟수: ${result.failureCount}
총 소요시간: ${result.totalSeconds}초
평균 성공시간: ${result.meanReactionTimeSeconds}초
성공 시간 목록(초): ${result.successTimes.join(', ')}
끝동작 유지 시간: ${result.holdMs}ms
손동작 인정 기준: ${result.gestureThreshold}
주의: ${result.note}
`;
  const blob=new Blob([text],{type:'text/plain;charset=utf-8'});
  const url=URL.createObjectURL(blob);
  ui.downloadArea.innerHTML=`<div class="small">성공 ${successes}회 · 실패 ${failCount}회 · 평균 성공시간 ${meanRt.toFixed(2)}초</div><a class="download" download="hand_rehab_result.txt" href="${url}">결과 TXT 다운로드</a>`;
  ui.modeLabel.textContent='훈련 종료';
  setTimeout(()=>{ try{ if(stream) stream.getTracks().forEach(t=>t.stop()); }catch(e){} }, 900);
  updateUI();
}
function updateUI(){ ui.state.textContent=state; ui.score.textContent=`${score}/${CONFIG.targetCount}`; if(ui.fail) ui.fail.textContent=`${failureCount}`; const acc=attempts?successes/attempts*100:(successes?100:0); ui.accuracy.textContent=attempts?`${acc.toFixed(0)}%`:'-'; const rt=mean(reactionTimes); ui.rt.textContent=rt?`${rt.toFixed(2)}초`:'-'; }
function drawScene(handData,m){
  ctx.clearRect(0,0,canvas.width,canvas.height);
  ctx.save(); if(CONFIG.mirrorView){ctx.translate(canvas.width,0);ctx.scale(-1,1);} ctx.drawImage(video,0,0,canvas.width,canvas.height); ctx.restore();
  ctx.fillStyle='rgba(0,0,0,.16)'; ctx.fillRect(0,0,canvas.width,canvas.height);
  drawGuide(); drawTargets(); drawParticles();
  if(handData&&handData.landmarks && now()>hideHandLandmarksUntil){ const lm=handData.landmarks.map(p=>({...p,x:CONFIG.mirrorView?1-p.x:p.x})); drawHand(lm); if(m){ const c=cursorPx(m); ctx.fillStyle=smoothedGesture>=CONFIG.gestureThreshold?'#33d17a':'#ffd166'; ctx.beginPath(); ctx.arc(c.x,c.y,13,0,Math.PI*2); ctx.fill(); ctx.strokeStyle='#fff'; ctx.lineWidth=3; ctx.stroke(); } }
  if(state==='complete'){ ctx.fillStyle='rgba(0,0,0,.58)'; ctx.fillRect(0,0,canvas.width,canvas.height); ctx.fillStyle='#33d17a'; ctx.font='bold 44px sans-serif'; ctx.textAlign='center'; ctx.fillText('훈련 완료',canvas.width/2,canvas.height/2-20); ctx.fillStyle='#fff'; ctx.font='24px sans-serif'; ctx.fillText(`성공 ${successes}/${CONFIG.targetCount} · 실패 ${failureCount} · 평균 ${mean(reactionTimes).toFixed(2)}초`,canvas.width/2,canvas.height/2+25); }
}
function drawGuide(){ ctx.strokeStyle='rgba(255,255,255,.33)'; ctx.lineWidth=2; ctx.setLineDash([8,8]); ctx.beginPath(); ctx.moveTo(canvas.width/2,0); ctx.lineTo(canvas.width/2,canvas.height); ctx.stroke(); ctx.beginPath(); ctx.moveTo(0,canvas.height/2); ctx.lineTo(canvas.width,canvas.height/2); ctx.stroke(); ctx.setLineDash([]); ctx.fillStyle='rgba(87,166,255,.10)'; ctx.fillRect(canvas.width*.12,canvas.height*.10,canvas.width*.76,canvas.height*.80); }
function drawBubble(o){
  if(!o)return;
  const x=o.x, y=o.y, r=o.r;
  const sprite = CONFIG.exerciseKey==='bubble_pinch' ? 'round_bubble_photo' : 'waterdrop_photo';
  const h = CONFIG.exerciseKey==='bubble_pinch' ? r*2.22 : r*2.75;
  const w = CONFIG.exerciseKey==='bubble_pinch' ? r*2.22 : r*2.25;
  if(drawSprite(sprite,x,y,w,h,1)) return;
  // Fallback vector drawing if image sprite is not loaded yet.
  ctx.save();
  ctx.shadowColor='rgba(30,160,255,.45)'; ctx.shadowBlur=18;
  const grad=ctx.createRadialGradient(x-r*.28,y-r*.36,r*.06,x,y+r*.10,r*1.18);
  grad.addColorStop(0,'rgba(255,255,255,.98)');
  grad.addColorStop(.18,'rgba(192,238,255,.96)');
  grad.addColorStop(.55,'rgba(70,183,255,.82)');
  grad.addColorStop(1,'rgba(0,93,205,.72)');
  ctx.fillStyle=grad;
  ctx.beginPath(); ctx.arc(x,y,r,0,Math.PI*2); ctx.fill();
  ctx.shadowBlur=0; ctx.strokeStyle='rgba(255,255,255,.86)'; ctx.lineWidth=Math.max(2,r*.045); ctx.stroke();
  ctx.restore();
}

function drawAirBubble(o, active=false){
  if(!o || o.popped) return;
  const x=o.x,y=o.y,r=o.r;
  const scale=active?2.36:2.20;
  if(drawSprite('round_bubble_photo',x,y,r*scale,r*scale,1)){
    if(active){ ctx.save(); ctx.strokeStyle='rgba(255,209,102,.98)'; ctx.lineWidth=5; ctx.beginPath(); ctx.arc(x,y,r*1.08,0,Math.PI*2); ctx.stroke(); ctx.restore(); }
    return;
  }
  ctx.save();
  const pulse = 1 + Math.sin(o.shimmer||0)*0.025;
  const rr = r*pulse;
  ctx.shadowColor='rgba(80,190,255,.28)'; ctx.shadowBlur=active?18:10;
  const grad=ctx.createRadialGradient(x-rr*.30,y-rr*.34,rr*.06,x,y,rr);
  grad.addColorStop(0,'rgba(255,255,255,.98)'); grad.addColorStop(.18,'rgba(228,249,255,.88)'); grad.addColorStop(.55,'rgba(144,219,255,.40)'); grad.addColorStop(1,'rgba(92,180,255,.14)');
  ctx.fillStyle=grad; ctx.beginPath(); ctx.arc(x,y,rr,0,Math.PI*2); ctx.fill();
  ctx.shadowBlur=0; ctx.strokeStyle=active?'rgba(255,209,102,.98)':'rgba(220,248,255,.95)'; ctx.lineWidth=active?5:3; ctx.beginPath(); ctx.arc(x,y,rr,0,Math.PI*2); ctx.stroke();
  ctx.restore();
}

function roundedPoly(points, radius){
  // Simple fallback polygon path with mild smoothing by quadratic corners.
  ctx.beginPath();
  for(let i=0;i<points.length;i++){
    const p=points[i], prev=points[(i-1+points.length)%points.length], next=points[(i+1)%points.length];
    const v1={x:prev.x-p.x,y:prev.y-p.y}, v2={x:next.x-p.x,y:next.y-p.y};
    const l1=Math.hypot(v1.x,v1.y)||1, l2=Math.hypot(v2.x,v2.y)||1;
    const a={x:p.x+v1.x/l1*radius,y:p.y+v1.y/l1*radius};
    const b={x:p.x+v2.x/l2*radius,y:p.y+v2.y/l2*radius};
    if(i===0) ctx.moveTo(a.x,a.y); else ctx.lineTo(a.x,a.y);
    ctx.quadraticCurveTo(p.x,p.y,b.x,b.y);
  }
  ctx.closePath();
}
function drawCup(o,filled=false,label='물컵'){
  if(!o)return;
  const x=o.x,y=o.y,r=o.r;
  const spriteName = filled ? 'glass_cup_full' : 'glass_cup_empty';
  if(drawSprite(spriteName,x,y,r*2.05,r*2.05,1)){
    return;
  }
  ctx.save();
  ctx.shadowColor='rgba(0,0,0,.28)'; ctx.shadowBlur=13; ctx.shadowOffsetY=5;
  // shadow / coaster
  ctx.fillStyle='rgba(0,0,0,.22)';
  ctx.beginPath(); ctx.ellipse(x,y+r*.84,r*.68,r*.18,0,0,Math.PI*2); ctx.fill();
  ctx.fillStyle='rgba(215,176,96,.20)';
  ctx.strokeStyle='rgba(242,208,120,.42)'; ctx.lineWidth=2;
  ctx.beginPath(); ctx.ellipse(x,y+r*.80,r*.78,r*.22,0,0,Math.PI*2); ctx.fill(); ctx.stroke();

  const topW=r*1.22, botW=r*.78, h=r*1.42;
  const topY=y-r*.76, botY=y+r*.66;
  const cupPath=[
    {x:x-topW/2,y:topY},{x:x+topW/2,y:topY},
    {x:x+botW/2,y:botY},{x:x-botW/2,y:botY}
  ];
  const glassGrad=ctx.createLinearGradient(x-topW/2,topY,x+topW/2,botY);
  glassGrad.addColorStop(0,'rgba(255,255,255,.48)');
  glassGrad.addColorStop(.18,'rgba(244,251,255,.22)');
  glassGrad.addColorStop(.48,'rgba(190,232,255,.18)');
  glassGrad.addColorStop(.78,'rgba(108,190,248,.15)');
  glassGrad.addColorStop(1,'rgba(255,255,255,.35)');
  ctx.fillStyle=glassGrad;
  ctx.strokeStyle='rgba(238,250,255,.94)'; ctx.lineWidth=Math.max(3,r*.055);
  roundedPoly(cupPath, r*.10); ctx.fill(); ctx.stroke();
  ctx.shadowBlur=0;

  // rim / base
  ctx.strokeStyle='rgba(255,255,255,.95)'; ctx.lineWidth=Math.max(2,r*.035);
  ctx.beginPath(); ctx.ellipse(x,topY,topW/2,r*.12,0,0,Math.PI*2); ctx.stroke();
  ctx.strokeStyle='rgba(210,239,255,.82)';
  ctx.beginPath(); ctx.ellipse(x,botY,botW/2,r*.08,0,0,Math.PI*2); ctx.stroke();

  // handle
  ctx.strokeStyle='rgba(235,250,255,.90)'; ctx.lineWidth=Math.max(3,r*.050);
  ctx.beginPath();
  ctx.moveTo(x+topW*.42, y-r*.18);
  ctx.bezierCurveTo(x+r*.92, y-r*.10, x+r*.92, y+r*.34, x+topW*.22, y+r*.30);
  ctx.stroke();
  ctx.strokeStyle='rgba(170,222,255,.34)'; ctx.lineWidth=Math.max(2,r*.028);
  ctx.beginPath();
  ctx.moveTo(x+topW*.37, y-r*.10);
  ctx.bezierCurveTo(x+r*.72, y-r*.02, x+r*.72, y+r*.24, x+topW*.20, y+r*.18);
  ctx.stroke();

  if(filled){
    const waterY=y-r*.20;
    const waterH=botY-waterY-r*.02;
    const waterGrad=ctx.createLinearGradient(x,waterY,x,botY);
    waterGrad.addColorStop(0,'rgba(140,228,255,.90)');
    waterGrad.addColorStop(.45,'rgba(79,190,255,.84)');
    waterGrad.addColorStop(1,'rgba(22,125,232,.72)');
    ctx.save(); roundedPoly(cupPath,r*.08); ctx.clip();
    ctx.fillStyle=waterGrad; ctx.fillRect(x-topW*.48,waterY,topW*.96,waterH);
    // water surface
    ctx.strokeStyle='rgba(238,255,255,.88)'; ctx.lineWidth=2;
    ctx.beginPath(); ctx.ellipse(x,waterY,topW*.39,r*.07,0,0,Math.PI*2); ctx.stroke();
    // subtle refraction
    ctx.fillStyle='rgba(255,255,255,.12)';
    ctx.beginPath(); ctx.ellipse(x-r*.08,y+r*.20,r*.22,r*.34,0,0,Math.PI*2); ctx.fill();
    ctx.restore();
  }
  // highlights
  ctx.strokeStyle='rgba(255,255,255,.72)'; ctx.lineWidth=Math.max(2,r*.026);
  ctx.beginPath(); ctx.moveTo(x-topW*.28,topY+r*.12); ctx.lineTo(x-botW*.22,botY-r*.12); ctx.stroke();
  ctx.strokeStyle='rgba(210,242,255,.55)'; ctx.lineWidth=Math.max(1.5,r*.018);
  ctx.beginPath(); ctx.moveTo(x+topW*.18,topY+r*.16); ctx.lineTo(x+botW*.12,botY-r*.16); ctx.stroke();

  ctx.restore();
}
function drawPitcher(o){
  if(!o)return;
  const x=o.x,y=o.y,r=o.r;
  ctx.save();
  ctx.shadowColor='rgba(0,0,0,.32)'; ctx.shadowBlur=12; ctx.shadowOffsetY=5;
  // Realistic plastic water bottle used as the pouring object.
  const bodyW=r*.88, bodyH=r*1.35, neckW=r*.36, neckH=r*.34, capH=r*.16;
  const top=y-bodyH*.56;
  const bottleGrad=ctx.createLinearGradient(x-bodyW/2,top,x+bodyW/2,y+bodyH*.55);
  bottleGrad.addColorStop(0,'rgba(245,252,255,.50)');
  bottleGrad.addColorStop(.25,'rgba(185,226,255,.30)');
  bottleGrad.addColorStop(.60,'rgba(90,184,255,.26)');
  bottleGrad.addColorStop(1,'rgba(255,255,255,.42)');
  ctx.fillStyle=bottleGrad; ctx.strokeStyle='rgba(235,250,255,.90)'; ctx.lineWidth=Math.max(3,r*.05);
  ctx.beginPath();
  ctx.moveTo(x-neckW/2, top);
  ctx.lineTo(x-neckW/2, top+neckH);
  ctx.bezierCurveTo(x-bodyW/2, top+neckH+r*.10, x-bodyW/2, y+bodyH*.30, x-bodyW*.34, y+bodyH*.50);
  ctx.lineTo(x+bodyW*.34, y+bodyH*.50);
  ctx.bezierCurveTo(x+bodyW/2, y+bodyH*.30, x+bodyW/2, top+neckH+r*.10, x+neckW/2, top+neckH);
  ctx.lineTo(x+neckW/2, top);
  ctx.closePath(); ctx.fill(); ctx.stroke();
  ctx.shadowBlur=0;
  // Water level inside bottle.
  ctx.save(); ctx.clip();
  const waterY=y+r*.12;
  ctx.fillStyle='rgba(80,205,255,.55)'; ctx.fillRect(x-bodyW*.46,waterY,bodyW*.92,y+bodyH*.50-waterY);
  ctx.strokeStyle='rgba(220,255,255,.65)'; ctx.lineWidth=2;
  ctx.beginPath(); ctx.ellipse(x,waterY,bodyW*.34,r*.06,0,0,Math.PI*2); ctx.stroke();
  ctx.restore();
  // Cap and label.
  ctx.fillStyle='rgba(55,145,255,.95)'; ctx.strokeStyle='rgba(230,245,255,.96)'; ctx.lineWidth=2;
  ctx.beginPath(); ctx.roundRect(x-neckW*.58, top-capH, neckW*1.16, capH, r*.04); ctx.fill(); ctx.stroke();
  const labelGrad=ctx.createLinearGradient(x-bodyW*.38,y-r*.02,x+bodyW*.38,y+r*.28);
  labelGrad.addColorStop(0,'rgba(255,255,255,.82)'); labelGrad.addColorStop(1,'rgba(170,225,255,.78)');
  ctx.fillStyle=labelGrad; ctx.strokeStyle='rgba(255,255,255,.85)';
  ctx.beginPath(); ctx.roundRect(x-bodyW*.35,y-r*.02,bodyW*.70,r*.28,r*.06); ctx.fill(); ctx.stroke();
  ctx.fillStyle='rgba(0,88,180,.95)'; ctx.font=`bold ${Math.max(11,Math.round(r*.17))}px sans-serif`; ctx.textAlign='center';
  ctx.fillText('WATER',x,y+r*.18);
  // Highlight and pouring hint.
  ctx.strokeStyle='rgba(255,255,255,.70)'; ctx.lineWidth=Math.max(2,r*.022);
  ctx.beginPath(); ctx.moveTo(x-bodyW*.27,top+neckH+r*.05); ctx.lineTo(x-bodyW*.20,y+bodyH*.35); ctx.stroke();
  ctx.fillStyle='#fff'; ctx.font=`bold ${Math.max(13,Math.round(r*.20))}px sans-serif`; ctx.textAlign='center';
  ctx.fillText('물병',x,y+r*1.03);
  ctx.restore();
}
function drawMouth(o){ if(!o)return; ctx.fillStyle=o.actual?'rgba(96,230,255,.24)':'rgba(255,209,102,.20)'; ctx.strokeStyle=o.actual?'rgba(96,230,255,.95)':'rgba(255,209,102,.90)'; ctx.lineWidth=4; ctx.setLineDash(o.actual?[]:[8,6]); ctx.beginPath(); ctx.arc(o.x,o.y,o.r,0,Math.PI*2); ctx.fill(); ctx.stroke(); ctx.setLineDash([]);  }
function drawTable(o){
  if(!o) return;
  const y=o.y || canvas.height*0.88;
  const h=canvas.height*0.16;
  if(drawSprite('table_wood', canvas.width/2, y+h*.18, canvas.width, h*1.35, .98)) { ctx.strokeStyle='rgba(255,255,255,.24)'; ctx.lineWidth=2; ctx.beginPath(); ctx.moveTo(0,y-h*.28); ctx.lineTo(canvas.width,y-h*.28); ctx.stroke(); return; }

  const top=y-h*0.28;
  const grad=ctx.createLinearGradient(0,top,0,y+h*0.68);
  grad.addColorStop(0,'rgba(150,106,63,.36)');
  grad.addColorStop(.5,'rgba(122,80,44,.62)');
  grad.addColorStop(1,'rgba(78,48,22,.82)');
  ctx.fillStyle=grad;
  ctx.fillRect(0,top,canvas.width,h);
  // wood plank lines for more realistic table impression
  for(let i=0;i<10;i++){
    const yy=top + (i+1)*(h/11);
    ctx.strokeStyle=i%2===0?'rgba(255,255,255,.06)':'rgba(45,22,8,.14)';
    ctx.lineWidth=i%2===0?1:1.2;
    ctx.beginPath(); ctx.moveTo(0,yy); ctx.lineTo(canvas.width,yy); ctx.stroke();
  }
  for(let i=0;i<7;i++){
    const xx=(i+1)*(canvas.width/8);
    ctx.strokeStyle='rgba(60,36,14,.16)'; ctx.lineWidth=1;
    ctx.beginPath(); ctx.moveTo(xx,top+4); ctx.lineTo(xx,y+h-6); ctx.stroke();
  }
  ctx.strokeStyle='rgba(255,255,255,.22)'; ctx.lineWidth=2;
  ctx.beginPath(); ctx.moveTo(0,top); ctx.lineTo(canvas.width,top); ctx.stroke();
}
function drawCupPlacementRing(cup){
  if(!cup) return;
  const x=cup.homeX, y=cup.homeY, r=cup.r*1.10;
  ctx.save();
  ctx.fillStyle='rgba(255,245,210,.10)';
  ctx.strokeStyle='rgba(255,209,102,.94)'; ctx.lineWidth=3; ctx.setLineDash([8,7]);
  ctx.beginPath(); ctx.ellipse(x,y+r*.62,r*.58,r*.16,0,0,Math.PI*2); ctx.fill(); ctx.stroke();
  ctx.setLineDash([]);

  ctx.restore();
}
function drawTargets(){
  if(!target)return;
  if(target.table) drawTable(target.table);
  if(target.kind==='bubble') drawBubble(target);
  if(target.kind==='air_bubbles' && target.bubbles){
    for(const b of target.bubbles){ drawAirBubble(b, b.id===target.activeId); }

  }
  if(target.cup && target.cup.attached) drawCupPlacementRing(target.cup);
  if(target.cup) drawCup(target.cup,target.cup.filled,'물컵');
  if(target.pitcher) drawPitcher(target.pitcher);
  if(target.mouth) drawMouth(target.mouth);
}
function drawParticles(){ particles=particles.filter(p=>p.life>0); for(const p of particles){ p.x+=p.vx; p.y+=p.vy; p.life--; ctx.fillStyle=`rgba(96,230,255,${p.life/50})`; ctx.beginPath(); ctx.arc(p.x,p.y,4,0,Math.PI*2); ctx.fill(); } }
function drawHand(lm){ const con=[[0,1],[1,2],[2,3],[3,4],[0,5],[5,6],[6,7],[7,8],[5,9],[9,10],[10,11],[11,12],[9,13],[13,14],[14,15],[15,16],[13,17],[17,18],[18,19],[19,20],[0,17]]; ctx.strokeStyle='rgba(51,209,122,.95)'; ctx.fillStyle='#33d17a'; ctx.lineWidth=3; for(const [a,b] of con){ ctx.beginPath(); ctx.moveTo(lm[a].x*canvas.width,lm[a].y*canvas.height); ctx.lineTo(lm[b].x*canvas.width,lm[b].y*canvas.height); ctx.stroke(); } for(let i=0;i<lm.length;i++){ const r=[4,8,12,16,20].includes(i)?6:4; ctx.beginPath(); ctx.arc(lm[i].x*canvas.width,lm[i].y*canvas.height,r,0,Math.PI*2); ctx.fill(); } }
function renderLoop(){
  if(!running)return; animationId=requestAnimationFrame(renderLoop);
  if(paused||!handLandmarker||video.readyState<2){ drawScene(null,null); return; }
  try{
    if(video.currentTime===lastVideoTime)return; lastVideoTime=video.currentTime; const frameTime=performance.now(); const result=handLandmarker.detectForVideo(video,frameTime); const faceResult=faceLandmarker?faceLandmarker.detectForVideo(video,frameTime):null; updateMouthTargetFromFace(faceResult); const hand=chooseHand(result);
    if(!hand){ if((trainingActive || calMode) && now()-lastHandFoundAt>2500)speakOnce('hand_not_found'); if(['cup_to_mouth','air_hold','hold_gesture'].includes(stage) || ['hold_gesture','do_gesture','air_bubble_hold'].includes(state)){ if(now()-lastHandFoundAt>5000) onFailure('손이 화면에서 사라졌습니다.'); } setInstruction('손이 보이지 않습니다','손 전체가 화면에 들어오도록 조정하세요.','bad'); drawScene(null,null); updateUI(); return; }
    if(hand.wrongHand){ speakOnce('wrong_hand'); setInstruction('선택한 손이 아닙니다','설정한 훈련 손을 카메라 앞에 보여 주세요.','bad'); drawScene(hand,null); return; }
    lastHandFoundAt=now(); const m=handMetrics(hand.landmarks); if(hand.score<CONFIG.minHandConfidence){ speakOnce('low_quality'); setInstruction('손 인식이 불안정합니다','조명, 손 가림, 카메라 각도를 조정하세요.','bad'); }
    processGame(m,hand.handed,hand.score); drawScene(hand,m); updateUI();
  }catch(e){ console.error(e); log(String(e)); }
}
function isMobileLike(){
  return /Android|iPhone|iPad|iPod|Mobile/i.test(navigator.userAgent) || matchMedia('(pointer: coarse)').matches;
}
async function requestLandscapeLock(){
  if(!isMobileLike()) return false;
  try{
    if(screen.orientation && screen.orientation.lock){
      await screen.orientation.lock('landscape');
      document.body.classList.add('landscapePreferred');
      updateVoiceStatus('가로 전체화면');
      return true;
    }
  }catch(e){
    console.info('orientation lock unavailable', e);
  }
  document.body.classList.add('landscapePreferred');
  return false;
}
function unlockOrientation(){
  try{ if(screen.orientation && screen.orientation.unlock) screen.orientation.unlock(); }catch(e){}
  document.body.classList.remove('landscapePreferred');
}
async function setCameraExpanded(expanded){
  const panel=ui.videoPanel;
  if(!panel) return;
  panel.classList.toggle('expandedCamera', !!expanded);
  document.body.classList.toggle('cameraExpanded', !!expanded);
  if(expanded){
    try{
      if(panel.requestFullscreen && !document.fullscreenElement){
        await panel.requestFullscreen({ navigationUI:'hide' }).catch(()=>panel.requestFullscreen().catch(()=>{}));
      }
    }catch(e){}
    await requestLandscapeLock();
  }else{
    unlockOrientation();
    try{ if(document.fullscreenElement && document.exitFullscreen) await document.exitFullscreen().catch(()=>{}); }catch(e){}
  }
  setTimeout(()=>forcePreviewDraw(), 120);
}
document.addEventListener('fullscreenchange', ()=>{
  const isFull=!!document.fullscreenElement;
  if(!isFull && ui.videoPanel){ ui.videoPanel.classList.remove('expandedCamera'); unlockOrientation(); }
  document.body.classList.toggle('cameraExpanded', isFull || !!ui.videoPanel?.classList.contains('expandedCamera'));
  setTimeout(()=>forcePreviewDraw(), 140);
});
window.addEventListener('orientationchange', ()=>setTimeout(()=>forcePreviewDraw(), 300));
window.addEventListener('resize', ()=>setTimeout(()=>forcePreviewDraw(), 180));

function bindButtons(){
  window.startCameraOnly = startCameraOnly;
  window.unlockAudio = unlockAudio;
  window.stopApp = stopApp;
  btn.camera.onclick = startCameraOnly;
  btn.sound.onclick = () => { stopAllSpeech('소리 테스트'); unlockAudio(true); };
  btn.fingerCal.onclick = startFingerCalibration;
  btn.train.onclick = startTraining;
  btn.abort.onclick = abortTraining;
  btn.pause.onclick = () => { stopAllSpeech('일시정지'); if(!trainingActive){ speakText('pause_only_training','일시정지는 훈련 중에만 사용합니다.',true); return; } paused=!paused; btn.pause.textContent=paused?'재개':'일시정지'; speakOnce(paused?'pause':'resume',true); };
  btn.stop.onclick = stopApp;
  if(btn.expand) btn.expand.onclick = () => setCameraExpanded(true);
  if(btn.shrink) btn.shrink.onclick = () => setCameraExpanded(false);
}
bindButtons();
setInstruction('① 카메라만 켜기를 누르세요','순서: ① 카메라만 켜기 → ② 손가락 동작 보정 또는 자동 인식 → ③ 훈련 시작. 선택한 훈련 목표는 훈련 시작 버튼을 누르면 먼저 표시되고, 시작 안내 뒤 판정됩니다.','info');
updateCalibrationStatus();
log(`훈련 과제: ${CONFIG.exercise.label}\n목표 수: ${CONFIG.targetCount}\n훈련 손: ${CONFIG.affectedHand==='Any'?'자동':CONFIG.affectedHand}\n주의: 조명, 손 가림, 카메라 각도에 따라 인식이 흔들릴 수 있습니다.`);
</script>
</body>
</html>
'''

html = HTML.replace("__CONFIG_JSON__", json.dumps(config, ensure_ascii=False))
components.html(html, height=940, scrolling=True)

with st.expander("임상/교육적 사용 시 주의점", expanded=False):
    st.markdown(
        """
        - 이 앱은 **교육용/피드백용 손 기능 재활 훈련 도구**입니다.
        - 단일 웹캠 기반 손 landmark 추정은 조명, 손 가림, 카메라 각도, 손 떨림, 마비 손의 변형에 영향을 받습니다.
        - 환자별 보정을 먼저 하면 손 기능 제한이 큰 환자에게 더 적합한 기준으로 훈련할 수 있습니다.
        - 정확한 임상 평가나 치료 효과 판정에 사용하려면 별도의 신뢰도·타당도 검증이 필요합니다.
        """
    )
