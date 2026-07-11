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


EXERCISES = {
    "bubble_grasp": {
        "label": "물방울 잡아 터뜨리기: 손 쥐기",
        "taskType": "bubble",
        "gesture": "grasp",
        "targetName": "물방울",
        "description": "손바닥 중심을 물방울에 가져간 뒤 손을 쥐면 성공합니다.",
        "clinicalGoal": "큰 물체 잡기, 손가락 굴곡, gross grasp 피드백",
    },
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

st.title("🖐️ 뇌졸중 환자 손 기능 재활 가상훈련")
st.caption("MediaPipe Hands Web 기반 · 스마트폰/태블릿 브라우저 실행 · Python MediaPipe/OpenCV 불필요")

with st.sidebar:
    st.header("훈련 설정")
    exercise_key = st.selectbox(
        "훈련 과제",
        options=list(EXERCISES.keys()),
        format_func=lambda k: EXERCISES[k]["label"],
        index=4,
    )
    affected_hand = st.radio(
        "훈련 손",
        options=["Right", "Left", "Any"],
        format_func=lambda v: {"Right": "오른손", "Left": "왼손", "Any": "자동/보이는 손"}[v],
        horizontal=True,
    )
    level = st.slider("난이도", min_value=1, max_value=5, value=2, step=1)
    level_cfg = LEVELS[level]
    target_count = st.slider("목표 물방울/공기방울/과제 수", min_value=3, max_value=30, value=level_cfg["targetCount"], step=1)
    hold_ms = st.slider("끝동작 유지 시간(ms)", min_value=200, max_value=2500, value=level_cfg["holdMs"], step=50)
    step_timeout_sec = st.slider("단계별 재시도 안내 시간(초)", min_value=10, max_value=60, value=30, step=5)
    gesture_threshold = st.slider("손동작 인정 기준", min_value=0.05, max_value=0.95, value=float(level_cfg["gestureThreshold"]), step=0.05)
    target_size_scale = st.slider("물방울/공기방울/물컵 크기 보정", min_value=0.60, max_value=1.80, value=1.00, step=0.05)
    speed_scale = st.slider("물방울/공기방울/물컵 속도 보정", min_value=0.00, max_value=2.50, value=1.00, step=0.10)
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
    1. 앱 안에서 **카메라/모델 시작**을 누르고 카메라 권한을 허용합니다.  
    2. 스마트폰/태블릿에서는 먼저 **소리 활성화/테스트**를 직접 누릅니다.  
    3. 손이 화면 중앙에 보이게 하고 **손 편 상태 보정**과 **쥔/집은 상태 보정**을 시행합니다.  
    4. 선택한 과제에 따라 물방울, 공기방울, 물컵 목표를 수행합니다.  
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
    "speedScale": float(speed_scale),
    "robustness": float(robustness),
    "minHandConfidence": float(min_hand_conf),
    "useFrontCamera": bool(use_front_camera),
    "mirrorView": bool(mirror_view),
    "trackMouth": bool(track_mouth),
    "soundMode": sound_mode,
    "audioAssets": load_audio_assets(),
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
  .overlayBanner { position:absolute; left:12px; right:12px; top:12px; padding:12px 14px; border-radius:16px; background:rgba(7,13,24,.80); backdrop-filter:blur(8px); border:1px solid rgba(255,255,255,.12); }
  #bigInstruction { font-size:clamp(21px,3.5vw,33px); font-weight:900; line-height:1.25; }
  #subInstruction { margin-top:4px; color:#d2e4ff; font-size:clamp(13px,2.3vw,17px); }
  .sidePanel { background:var(--panel); border:1px solid rgba(255,255,255,.10); border-radius:18px; padding:14px; }
  .buttons { display:flex; flex-wrap:wrap; gap:8px; margin-bottom:10px; }
  button { appearance:none; border:0; border-radius:14px; padding:11px 13px; font-weight:850; background:#eaf4ff; color:#06101d; min-height:42px; cursor:pointer; }
  button.primary { background:var(--green); } button.blue { background:var(--blue); color:#fff; } button.warn { background:var(--yellow); } button.danger { background:var(--red); color:#fff; }
  .metric { display:grid; grid-template-columns:1fr auto; gap:8px; padding:9px 0; border-bottom:1px solid rgba(255,255,255,.08); font-size:15px; }
  .metric b { font-size:18px; }
  .statusBox { margin-top:10px; padding:10px; border-radius:14px; background:rgba(255,255,255,.06); min-height:88px; white-space:pre-line; color:#dceaff; font-size:14px; }
  .bar { height:13px; border-radius:999px; background:rgba(255,255,255,.12); overflow:hidden; margin-top:6px; }
  .fill { height:100%; width:0%; background:var(--green); transition:width .12s linear; }
  .small { color:var(--muted); font-size:12px; line-height:1.45; }
  .calBox { margin-top:10px; border-radius:14px; padding:10px; background:rgba(255,255,255,.04); border:1px solid rgba(255,255,255,.08); }
  a.download { display:block; margin-top:8px; color:#9fd0ff; word-break:break-all; }
</style>
</head>
<body>
<div class="app">
  <div class="topbar"><div class="title">🖐️ 손 기능 재활 가상훈련</div><div class="pill" id="modeLabel">로딩 중...</div></div>
  <div class="grid">
    <div class="videoPanel">
      <video id="webcam" autoplay playsinline muted></video>
      <canvas id="outputCanvas"></canvas>
      <div class="overlayBanner"><div id="bigInstruction">카메라/모델 시작을 누르세요</div><div id="subInstruction">소리 활성화 후 손을 화면 중앙에 보여 주세요.</div></div>
    </div>
    <div class="sidePanel">
      <div class="buttons">
        <button id="btnStart" class="primary">카메라/모델 시작</button>
        <button id="btnSound" class="blue">소리 활성화/테스트</button>
        <button id="btnOpenCal" class="warn">손 편 상태 보정</button>
        <button id="btnCloseCal" class="warn">쥔/집은 상태 보정</button>
        <button id="btnReset" class="blue">훈련 새로 시작</button>
        <button id="btnPause">일시정지</button>
        <button id="btnStop" class="danger">카메라 정지</button>
      </div>
      <div class="metric"><span>현재 단계</span><b id="stateText">대기</b></div>
      <div class="metric"><span>성공/목표</span><b id="scoreText">0</b></div>
      <div class="metric"><span>실패 횟수</span><b id="failText">0</b></div>
      <div class="metric"><span>손동작 점수</span><b id="gestureText">0%</b></div>
      <div class="metric"><span>현재 손</span><b id="handText">-</b></div>
      <div class="metric"><span>성공률</span><b id="accuracyText">-</b></div>
      <div class="metric"><span>평균 반응시간</span><b id="rtText">-</b></div>
      <div class="calBox"><b>환자별 보정 상태</b><div class="small">손 편 상태와 쥔/집은 상태를 보정하면 마비 손의 변형과 제한된 움직임을 더 잘 반영합니다.</div><div class="small" id="calStatus">기본값 사용 중</div><div class="bar"><div class="fill" id="calFill"></div></div></div>
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
const video = document.getElementById('webcam');
const canvas = document.getElementById('outputCanvas');
const ctx = canvas.getContext('2d');
const ui = {
  modeLabel: document.getElementById('modeLabel'), big: document.getElementById('bigInstruction'), sub: document.getElementById('subInstruction'), state: document.getElementById('stateText'), score: document.getElementById('scoreText'), fail: document.getElementById('failText'), gesture: document.getElementById('gestureText'), hand: document.getElementById('handText'), accuracy: document.getElementById('accuracyText'), rt: document.getElementById('rtText'), log: document.getElementById('logBox'), calStatus: document.getElementById('calStatus'), calFill: document.getElementById('calFill'), downloadArea: document.getElementById('downloadArea')
};
const btn = { start:document.getElementById('btnStart'), sound:document.getElementById('btnSound'), openCal:document.getElementById('btnOpenCal'), closeCal:document.getElementById('btnCloseCal'), reset:document.getElementById('btnReset'), pause:document.getElementById('btnPause'), stop:document.getElementById('btnStop') };

const messages = {
  sound_test:'소리 안내가 활성화되었습니다.',
  start_camera:'카메라를 시작합니다. 손을 화면 중앙에 보여 주세요.',
  hand_not_found:'손이 보이지 않습니다. 손 전체가 화면에 들어오도록 조정하세요.',
  wrong_hand:'선택한 손이 아닙니다. 훈련 손을 다시 확인하세요.',
  low_quality:'손 인식이 불안정합니다. 조명을 밝게 하고 손 가림을 줄여 주세요.',
  open_cal_start:'손을 최대한 편 상태로 유지하세요.',
  close_cal_start: CONFIG.exercise.gesture==='pinch' ? '엄지와 검지를 맞댄 상태로 유지하세요.' : '손을 쥐는 상태로 유지하세요.',
  cal_done:'보정이 완료되었습니다.',

  seek_target:'목표 위치로 손을 가져가세요.',
  now_gesture: CONFIG.exercise.gesture==='pinch' ? '엄지와 검지를 맞대어 집으세요.' : (CONFIG.exercise.gesture==='open' ? '손을 충분히 펴세요.' : '손을 쥐세요.'),
  hold_gesture:'좋습니다. 끝동작을 그대로 유지하세요.',
  success:'정상적으로 성공했습니다.',
  complete:'모든 훈련이 끝났습니다. 결과를 확인하세요.',

  cup_reach:'물컵으로 손을 가져가세요.',
  cup_grasp:'물컵을 잡으세요. 손을 쥔 상태를 유지하세요.',
  cup_to_mouth:'좋습니다. 물컵을 실제 입 위치까지 천천히 옮기세요.',
  cup_drink_hold:'입 위치에 도착했습니다. 그 위치에서 잠시 멈추세요.',
  mouth_not_found:'입 위치가 보이지 않습니다. 얼굴과 입이 화면에 보이도록 조정하세요.',

  air_bubble_seek:'얼굴 아래에 퍼져 있는 물방울 중 하나로 손을 천천히 가져가세요.',
  air_bubble_grasp:'물방울 안에서 손을 쥐세요. 손을 쥔 상태를 잠시 유지하면 물방울이 터집니다.',
  air_bubble_hold:'좋습니다. 물방울을 잡은 상태를 잠시 유지하세요.',

  pause:'훈련을 일시정지합니다.',
  resume:'훈련을 다시 시작합니다.'
};

let handLandmarker=null, faceLandmarker=null, stream=null, running=false, paused=false, animationId=null, lastVideoTime=-1;
let audioCtx=null, soundUnlocked=false, lastSpeakKey='', lastSpeakAt=0;
let speechQueue=[], speechActive=false, speechMaxQueue=4;
let state='idle', score=0, attempts=0, successes=0, failureCount=0, reactionTimes=[], successTimes=[], gameStartTime=0;
let target=null, stage='none', holdStart=null, overlapStart=null, reactionStart=null, lastStatusVoice=0;
let targetSerial=0, lastStepId='', stepStartedAt=0, lastFailureAt=0;
let openMetrics=null, closeMetrics=null, calMode=null, calSamples=[], calStart=0;
let smoothLandmarks=null, smoothedGesture=0, smoothedCursor=null, lastHandFoundAt=0, neutralTilt=null;
let currentMouth=null, smoothedMouth=null, mouthDetectedAt=0, lastMouthVoice=0, successLock=false;
let particles=[];

ui.modeLabel.textContent = `준비됨 · ${CONFIG.exercise.label} · ${CONFIG.levelConfig.name}`;

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

async function unlockAudio(){
  try{
    audioCtx = audioCtx || new (window.AudioContext||window.webkitAudioContext)();
    if(audioCtx.state==='suspended') await audioCtx.resume();
    beep(660,.08,.06); setTimeout(()=>beep(880,.08,.06),110);
    soundUnlocked=true; speakOnce('sound_test', true);
    setInstruction('소리 안내가 활성화되었습니다','말소리가 안 들려도 신호음·진동·화면 안내가 함께 작동합니다.','ready');
  }catch(e){ setInstruction('소리 활성화가 제한되었습니다','무음모드와 미디어 볼륨을 확인하세요.','warn'); }
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
function speakText(key, text, force=false){
  const t=now();
  if(!force && key===lastSpeakKey && t-lastSpeakAt<6200) return;
  lastSpeakKey=key; lastSpeakAt=t;
  ui.sub.textContent=text;
  if(navigator.vibrate){
    if(['success','complete'].includes(key) || key.startsWith('rep_success')) navigator.vibrate([70,40,70]);
    else if(['wrong_hand','hand_not_found','low_quality'].includes(key) || key.startsWith('fail')) navigator.vibrate([140,60,140]);
    else navigator.vibrate(45);
  }
  playMessage(key,text);
}
function playMessage(key,text){
  if(CONFIG.soundMode==='silent') return;
  if(!soundUnlocked){ toneFor(key); return; }
  const asset=AUDIO_ASSETS[key];
  if(CONFIG.soundMode==='audio_first' && asset && asset.data){ try{ const a=new Audio(asset.data); a.play().catch(()=>fallbackSpeechOrTone(text,key)); return; }catch(e){} }
  fallbackSpeechOrTone(text,key);
}
function fallbackSpeechOrTone(text,key){
  if(CONFIG.soundMode==='tone_only' || !('speechSynthesis' in window)){ toneFor(key); return; }
  try{ enqueueSpeech(text,key); }catch(e){ toneFor(key); }
}
function enqueueSpeech(text,key){
  const important = key.startsWith('task_intro') || key.startsWith('task_begin') || key.startsWith('complete') || key.startsWith('fail');
  if(important){
    speechQueue = speechQueue.filter(item => !(item.key.startsWith('stage_') || item.key==='air_bubble_seek'));
  }else if(speechQueue.length >= speechMaxQueue){
    speechQueue = speechQueue.slice(-speechMaxQueue+1);
  }
  speechQueue.push({text,key});
  drainSpeechQueue();
}
function drainSpeechQueue(){
  if(speechActive || speechQueue.length===0) return;
  const item = speechQueue.shift();
  speechActive = true;
  try{
    const u=new SpeechSynthesisUtterance(item.text);
    u.lang='ko-KR'; u.rate=.88; u.pitch=1.0; u.volume=1.0;
    const done=()=>{ speechActive=false; setTimeout(drainSpeechQueue,80); };
    u.onend=done; u.onerror=()=>{ toneFor(item.key); done(); };
    window.speechSynthesis.speak(u);
    setTimeout(()=>{ if(speechActive && window.speechSynthesis.speaking===false){ toneFor(item.key); speechActive=false; drainSpeechQueue(); } },900);
  }catch(e){ speechActive=false; toneFor(item.key); drainSpeechQueue(); }
}

async function startApp(){
  if(running) return;
  try{
    setInstruction('버튼 입력이 확인되었습니다','MediaPipe Hands 모듈과 모델을 불러오는 중입니다. 잠시 기다려 주세요.','info');
    log('카메라/모델 시작 버튼이 눌렸습니다. MediaPipe Hands 모듈을 불러오는 중입니다.');
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
    running=true; paused=false; resetGame(false); speakOnce('start_camera',true); speakText('task_begin_'+targetSerial, taskIntroText(), true); renderLoop();
  }catch(e){ console.error(e); setInstruction('카메라 또는 모델을 시작할 수 없습니다','HTTPS 접속, 카메라 권한, 브라우저를 확인하세요.','bad'); log(String(e)); }
}
function stopApp(){ running=false; paused=false; if(animationId) cancelAnimationFrame(animationId); if(stream) stream.getTracks().forEach(t=>t.stop()); stream=null; setInstruction('카메라가 정지되었습니다','다시 시작하려면 카메라/모델 시작을 누르세요.','info'); }
function resetGame(announce=true){
  score=0; attempts=0; successes=0; failureCount=0; reactionTimes=[]; successTimes=[]; target=null; stage='none'; holdStart=null; overlapStart=null; reactionStart=null; particles=[]; gameStartTime=now(); state='waiting_hand'; ui.downloadArea.innerHTML=''; neutralTilt=null; successLock=false; targetSerial=0; lastStepId=''; stepStartedAt=now(); lastFailureAt=0; updateUI(); spawnTaskTarget();
  if(announce){
    speakText('task_intro_'+targetSerial, taskIntroText(), true);
  }
}
function gestureActionText(){
  if(CONFIG.exercise.gesture==='pinch') return '엄지와 검지를 맞대어 집기 동작을 하세요';
  if(CONFIG.exercise.gesture==='open') return '손을 충분히 펴세요';
  return '손을 쥐세요';
}
function taskIntroText(){
  if(CONFIG.exercise.taskType==='hand_bubbles'){
    return `물방울 잡아 터뜨리기 훈련을 시작합니다. 목표는 총 ${CONFIG.targetCount}개입니다. 먼저 손을 편안하게 펴고 화면 안에 보여 주세요. 화면 속 얼굴 아래쪽에 여러 개의 물방울이 나타납니다. 물방울 하나를 선택해서 손바닥 중심을 물방울 안으로 천천히 가져가세요. 손바닥 점이 닿는 것만으로는 성공이 아닙니다. 물방울 안에서 손가락을 굽혀 손을 쥐고, 안내가 끝날 때까지 잠시 유지해야 물방울이 터집니다. 물방울이 터지면 손을 다시 편안하게 펴고 다음 물방울로 이동하세요. 모든 물방울이 사라지면 성공적으로 종료됩니다.`;
  }
  return `${CONFIG.exercise.label} 훈련을 시작합니다. 목표는 총 ${CONFIG.targetCount}회입니다. 환자분은 화면 안내에 따라 한 단계씩 수행하고, 성공하면 다시 처음 자세에서 같은 과정을 반복합니다. ${taskStartText()}`;
}
function taskStartText(){
  const rep=Math.min(score+1, CONFIG.targetCount);
  const t=CONFIG.exercise.taskType;
  if(t==='cup_drink') return `${rep}회차입니다. 먼저 손을 물컵으로 가져가세요. 물컵을 잡은 뒤, 실제 입 위치로 옮기고 잠시 멈추세요.`;
  if(t==='hand_bubbles') return `남은 물방울 중 하나로 손을 천천히 이동하세요. 물방울 안에 들어가면 손가락을 굽혀 쥐고, 잠시 유지합니다.`;
  return `${rep}회차입니다. 손을 ${CONFIG.exercise.targetName} 위치로 가져간 뒤, ${gestureActionText()}. 끝동작은 잠시 유지합니다.`;
}
function taskStartMessage(){ const t=CONFIG.exercise.taskType; if(t==='cup_drink') return 'cup_reach'; if(t==='hand_bubbles') return 'air_bubble_seek'; return 'seek_target'; }

function startCalibration(mode){
  if(!running) return;
  calMode=mode; calSamples=[]; calStart=now(); state=mode==='open'?'cal_open':'cal_close'; ui.calFill.style.width='0%';
  if(mode==='open') speakOnce('open_cal_start',true); else speakOnce('close_cal_start',true);
  setInstruction(mode==='open'?'손을 편 상태로 유지하세요':(CONFIG.exercise.gesture==='pinch'?'엄지와 검지를 맞대세요':'손을 쥐세요'),'2초 동안 카메라 앞에서 유지합니다.','warn');
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
function gestureScore(m, gesture=CONFIG.exercise.gesture){
  if(gesture==='open'){ const closeVal=closeMetrics?.fingertipAvg ?? 1.05; const openVal=openMetrics?.fingertipAvg ?? 1.75; return clamp((m.fingertipAvg-closeVal)/Math.max(.12,openVal-closeVal),0,1); }
  if(gesture==='pinch'){ const openVal=openMetrics?.pinch ?? .75; const closeVal=closeMetrics?.pinch ?? .18; return clamp((openVal-m.pinch)/Math.max(.08,openVal-closeVal),0,1); }
  const openVal=openMetrics?.fingertipAvg ?? 1.75; const closeVal=closeMetrics?.fingertipAvg ?? 1.05; return clamp((openVal-m.fingertipAvg)/Math.max(.12,openVal-closeVal),0,1);
}
function updateGestureDisplay(m){ smoothedGesture=lerp(smoothedGesture, gestureScore(m), .22); ui.gesture.textContent=`${Math.round(smoothedGesture*100)}%`; }
function canvasPoint(p){ return {x:(CONFIG.mirrorView ? 1-p.x : p.x)*canvas.width, y:p.y*canvas.height}; }
function cursorPx(m){ const p=canvasPoint(m.cursor); if(!smoothedCursor) smoothedCursor=p; smoothedCursor={x:lerp(smoothedCursor.x,p.x,.30), y:lerp(smoothedCursor.y,p.y,.30)}; return smoothedCursor; }
function targetRadius(){ return CONFIG.levelConfig.targetRadius*CONFIG.targetSizeScale; }
function randomTarget(r){ const margin=r+28; return {x:margin+Math.random()*Math.max(20,canvas.width-margin*2), y:margin+Math.random()*Math.max(20,canvas.height-margin*2), r, vx:(Math.random()*2-1)*CONFIG.levelConfig.speed*CONFIG.speedScale, vy:(Math.random()*2-1)*CONFIG.levelConfig.speed*CONFIG.speedScale}; }
function mouthFallback(r){ return {x:canvas.width*.74,y:canvas.height*.25,r:r*.78,actual:false}; }
function spawnTaskTarget(){
  const r=targetRadius(); const type=CONFIG.exercise.taskType;
  holdStart=null; overlapStart=null; reactionStart=now(); successLock=false; targetSerial++; lastStepId=''; stepStartedAt=now();
  if(type==='bubble'){ target=randomTarget(r); target.kind='bubble'; stage='seek'; state='seek_target'; }
  else if(type==='cup_drink'){ target={cup:{x:canvas.width*.25,y:canvas.height*.64,r:r*.82,attached:false}, mouth:mouthFallback(r)}; stage='cup_reach'; state='cup_reach'; }
  else if(type==='hand_bubbles'){ target={kind:'air_bubbles', bubbles:[], initialized:false, lastPop:null, activeId:null, anchor:{x:canvas.width*.50,y:canvas.height*.34}, r:r*.52}; stage='air_seek'; state='air_bubble_seek'; }
  else { target=randomTarget(r); target.kind='bubble'; stage='seek'; state='seek_target'; }
}
function moveTarget(t){ if(!t||!t.vx) return; t.x+=t.vx; t.y+=t.vy; if(t.x<t.r||t.x>canvas.width-t.r) t.vx*=-1; if(t.y<t.r||t.y>canvas.height-t.r) t.vy*=-1; }
function insidePoint(p,obj,scale=1.0){ return Math.hypot(p.x-obj.x,p.y-obj.y) <= obj.r*scale; }
function holdProgress(){ return holdStart ? (now()-holdStart)/CONFIG.holdMs : 0; }
function beginHold(){ if(!holdStart){ holdStart=now(); speakOnce('hold_gesture'); } }
function resetHold(){ holdStart=null; }
function resetCurrentAttempt(){
  holdStart=null; overlapStart=null; reactionStart=now(); neutralTilt=null; successLock=false;
  if(CONFIG.exercise.taskType==='hand_bubbles' && target && target.kind==='air_bubbles'){
    target.activeId = null; stage='air_seek'; state='air_bubble_seek';
  }else{
    spawnTaskTarget();
  }
}
function onFailure(reason='잘못 수행되었습니다.'){
  if(state==='complete' || now()-lastFailureAt<4500) return;
  lastFailureAt=now(); attempts++; failureCount++;
  const remain = CONFIG.exercise.taskType==='hand_bubbles' ? remainingBubbles() : Math.max(0, CONFIG.targetCount-score);
  setInstruction('다시 시도하세요', `${reason} 성공으로 기록하지 않습니다. 남은 목표를 다시 수행하세요.`, 'bad');
  speakText('fail_'+targetSerial, `${reason} 이번 시도는 성공으로 기록하지 않습니다. 준비 자세로 돌아온 뒤 다시 수행하세요. 남은 목표는 ${remain}개입니다.`, true);
  resetCurrentAttempt();
  updateUI();
}
function checkStepTimeout(){
  const id = stage + '|' + state;
  if(id!==lastStepId){ lastStepId=id; stepStartedAt=now(); }
  const active = ['do_gesture','hold_gesture','cup_reach','cup_to_mouth','air_bubble_seek','air_bubble_grasp','air_bubble_hold'];
  const isActive = active.includes(state) || ['cup_reach','cup_to_mouth','air_seek','air_hold'].includes(stage);
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
  setInstruction('정상적으로 성공했습니다', `물방울 ${score}개를 터뜨렸습니다. 남은 물방울은 ${remain}개입니다.`, 'ready');
  speakText('rep_success_'+score, `정상적으로 성공했습니다. 물방울 ${score}개를 터뜨렸습니다. 남은 물방울은 ${remain}개입니다. 처음 자세에서 다음 물방울을 계속 터뜨리세요.`, true);
  setTimeout(()=>{ if(running&&!paused&&state!=='complete'){
    if(CONFIG.exercise.taskType==='hand_bubbles' && target && target.kind==='air_bubbles'){ holdStart=null; successLock=false; stage='air_seek'; state='air_bubble_seek'; reactionStart=now(); target.activeId=null; }
    else{ spawnTaskTarget(); speakText('rep_start_'+targetSerial, taskStartText(), true); }
  } }, 1200);
}
function addParticles(){ const pop=target?.lastPop || target; const px=(pop?.x||target?.x||target?.cup?.x||canvas.width/2), py=(pop?.y||target?.y||target?.cup?.y||canvas.height/2); for(let i=0;i<24;i++){ particles.push({x:px, y:py, vx:(Math.random()*2-1)*3.4, vy:(Math.random()*2-1)*3.4, life:32+Math.random()*24}); } }

function processBubble(m){
  if(!target) spawnTaskTarget(); moveTarget(target);
  const c=cursorPx(m); const inside=insidePoint(c,target,1.05); const g=smoothedGesture>=CONFIG.gestureThreshold || CONFIG.level===1;
  if(!inside){ resetHold(); if(now()-lastStatusVoice>4500){speakOnce('seek_target'); lastStatusVoice=now();} setInstruction(`1단계: ${CONFIG.exercise.targetName}에 손을 가져가세요`,'목표 안에 손이 들어가면 다음 단계 안내가 나옵니다.','info'); state='seek_target'; return; }
  if(!g){ resetHold(); speakOnce('now_gesture'); const action=CONFIG.exercise.gesture==='pinch'?'엄지와 검지를 맞대세요':CONFIG.exercise.gesture==='open'?'손을 충분히 펴세요':'손을 쥐세요'; setInstruction(`2단계: ${action}`,'목표 안에서 끝동작을 수행하고 잠시 유지합니다.','action'); state='do_gesture'; return; }
  beginHold(); const hp=holdProgress(); setInstruction('3단계: 끝동작을 잠시 유지하세요',`${Math.round(clamp(hp,0,1)*100)}%`, 'warn'); state='hold_gesture'; if(hp>=1) onSuccess();
}

function makeAirBubble(id,x,y,r){
  const sp=CONFIG.levelConfig.speed*CONFIG.speedScale;
  const angle=Math.random()*Math.PI*2;
  const speed=sp*(0.35+Math.random()*0.55);
  return {id,x,y,r,baseX:x,baseY:y,vx:Math.cos(angle)*speed,vy:Math.sin(angle)*speed,popped:false,locked:false, shimmer:Math.random()*Math.PI*2};
}
function bubbleAnchor(){
  const mouthRef = (target?.mouth && target.mouth.actual!==false) ? target.mouth : smoothedMouth;
  if(CONFIG.trackMouth && mouthRef){
    return {x: mouthRef.x, y: clamp(mouthRef.y + targetRadius()*1.9, canvas.height*0.28, canvas.height*0.72)};
  }
  return {x: canvas.width*0.5, y: canvas.height*0.36};
}
function buildBubbleCluster(){
  if(!target || target.kind!=='air_bubbles') return;
  const anchor = bubbleAnchor();
  target.anchor = anchor;
  const count = CONFIG.targetCount;
  const baseR = target.r || targetRadius()*0.52;
  target.bubbles = [];
  const areaW = clamp(baseR*(Math.ceil(Math.sqrt(count))*3.45), baseR*5.5, canvas.width*0.86);
  const areaH = clamp(baseR*(Math.ceil(count/Math.max(2,Math.ceil(Math.sqrt(count))))*3.25), baseR*4.8, canvas.height*0.58);
  const left = clamp(anchor.x-areaW/2, baseR+16, canvas.width-baseR-16);
  const right = clamp(anchor.x+areaW/2, baseR+16, canvas.width-baseR-16);
  const top = clamp(anchor.y-baseR*.35, baseR+16, canvas.height-baseR-16);
  const bottom = clamp(anchor.y+areaH, baseR+16, canvas.height-baseR-16);
  let attempts=0;
  let minGapFactor=1.55;
  while(target.bubbles.length<count && attempts<3000){
    attempts++;
    if(attempts===1200) minGapFactor=1.35;
    if(attempts===2200) minGapFactor=1.18;
    const rr = baseR*(0.90 + Math.random()*0.20);
    const x = clamp(left + Math.random()*Math.max(baseR*2,right-left), rr+16, canvas.width-rr-16);
    const y = clamp(top + Math.random()*Math.max(baseR*2,bottom-top), rr+16, canvas.height-rr-16);
    let ok=true;
    for(const existing of target.bubbles){
      const minD=(existing.r+rr)*minGapFactor;
      if(Math.hypot(existing.x-x, existing.y-y) < minD){ ok=false; break; }
    }
    if(ok){ target.bubbles.push(makeAirBubble(`${targetSerial}_${target.bubbles.length}_${Math.random()}`, x, y, rr)); }
  }
  // Fallback grid if the screen is too small for the requested number.
  let i=target.bubbles.length;
  const cols=Math.max(2, Math.ceil(Math.sqrt(count)));
  while(i<count){
    const col=i%cols, row=Math.floor(i/cols);
    const x=clamp(anchor.x + (col-(cols-1)/2)*baseR*2.65, baseR+16, canvas.width-baseR-16);
    const y=clamp(anchor.y + row*baseR*2.55, baseR+16, canvas.height-baseR-16);
    target.bubbles.push(makeAirBubble(`${targetSerial}_${i}_${Math.random()}`, x, y, baseR));
    i++;
  }
  target.initialized = true;
}
function ensureAirBubbles(){
  if(!target || target.kind!=='air_bubbles') return;
  if(!target.initialized || !target.bubbles || target.bubbles.length===0){
    buildBubbleCluster();
  }
}
function moveAirBubbles(){
  if(!target?.bubbles) return;
  const anchor = bubbleAnchor();
  target.anchor = anchor;
  for(const b of target.bubbles){
    if(b.popped) continue;
    b.shimmer += 0.04;
    if(CONFIG.speedScale>0){
      b.baseX += b.vx*0.35;
      b.baseY += b.vy*0.35;
      const maxDX = target.r*2.4, maxDY = target.r*1.8;
      b.baseX = clamp(b.baseX, anchor.x-maxDX, anchor.x+maxDX);
      b.baseY = clamp(b.baseY, anchor.y-target.r*0.5, anchor.y+maxDY);
      if(b.baseX<=anchor.x-maxDX || b.baseX>=anchor.x+maxDX) b.vx*=-1;
      if(b.baseY<=anchor.y-target.r*0.5 || b.baseY>=anchor.y+maxDY) b.vy*=-1;
    }
    b.x = lerp(b.x, b.baseX, 0.12);
    b.y = lerp(b.y, b.baseY, 0.12);
  }
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
function processHandBubbles(m){
  if(!target || target.kind!=='air_bubbles') spawnTaskTarget();
  ensureAirBubbles();
  moveAirBubbles();
  const c=cursorPx(m);
  const b=nearestAirBubble(c);
  target.activeId = b ? b.id : null;
  const g=smoothedGesture>=CONFIG.gestureThreshold;
  const remain = remainingBubbles();
  if(remain<=0){ completeGame(); return; }
  if(!b){
    resetHold();
    if(now()-lastStatusVoice>5200){speakText('stage_bubble_seek_'+score, `물방울 하나를 선택해 손바닥 중심을 물방울 안으로 천천히 가져가세요. 손은 아직 편 상태로 준비합니다. 남은 물방울은 ${remain}개입니다.`, false); lastStatusVoice=now();}
    setInstruction('1단계: 물방울 하나에 손을 가져가세요',`얼굴 아래쪽에 퍼져 있는 남은 물방울 ${remain}개 중 하나 안으로 손을 천천히 이동합니다.`, 'info');
    stage='air_seek'; state='air_bubble_seek'; return;
  }
  if(!g){
    resetHold();
    speakText('stage_bubble_grasp_'+score, `물방울 안에 손이 들어왔습니다. 이제 손가락을 굽혀 손을 쥐세요. 손바닥 점만 닿아서는 성공하지 않습니다.`, false);
    setInstruction('2단계: 손가락을 굽혀 쥐세요','손바닥 점이 닿는 것만으로는 성공하지 않습니다. 설정 기준 이상으로 손을 쥐어야 합니다.','action');
    stage='air_grasp'; state='air_bubble_grasp'; return;
  }
  if(!holdStart){ holdStart=now(); speakText('stage_bubble_hold_'+score, '좋습니다. 손을 쥔 상태를 그대로 유지하세요. 유지 시간이 채워지면 물방울이 터집니다.', false); }
  const hp=holdProgress();
  setInstruction('3단계: 잡은 상태를 잠시 유지하세요',`물방울 터뜨리기 ${Math.round(clamp(hp,0,1)*100)}% · 남은 물방울 ${remain}개`, 'warn');
  stage='air_hold'; state='air_bubble_hold';
  if(hp>=1 && !b.popped && !b.locked){
    b.locked = true;
    b.popped = true;
    target.lastPop={x:b.x,y:b.y,r:b.r};
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
        const baseR=targetRadius()*0.50;
        const r=clamp(Math.max(baseR, mouthWidth*1.20), targetRadius()*0.42, targetRadius()*0.90);
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
  const c=cursorPx(m); const cup=target.cup, mouth=target.mouth; const g=smoothedGesture>=CONFIG.gestureThreshold || CONFIG.level===1;
  if(stage==='cup_reach'){
    if(!insidePoint(c,cup,1.08)){ resetHold(); speakOnce('cup_reach'); setInstruction('1단계: 물컵으로 손을 가져가세요','손바닥 중심이 물컵 안에 들어가도록 천천히 이동합니다.','info'); return; }
    if(!g){ resetHold(); speakOnce('cup_grasp'); setInstruction('2단계: 물컵을 잡으세요','손을 쥔 상태를 유지하면 컵이 손에 붙습니다.','action'); return; }
    beginHold(); setInstruction('물컵을 잡은 상태를 유지하세요',`${Math.round(clamp(holdProgress(),0,1)*100)}%`, 'warn'); if(holdProgress()>=1){ cup.attached=true; stage='cup_to_mouth'; resetHold(); speakText('stage_cup_to_mouth_'+targetSerial, '좋습니다. 이제 물컵을 실제 입 위치까지 천천히 옮기세요.', true); }
    return;
  }
  if(stage==='cup_to_mouth'){
    cup.x=c.x; cup.y=c.y;
    if(!mouthReady()){ resetHold(); setInstruction('입 위치가 보이도록 얼굴을 보여 주세요','얼굴과 입 주변이 화면에 보이면 실제 입 위치 목표가 표시됩니다.','warn'); return; }
    if(!insidePoint(c,mouth,.95)){ resetHold(); setInstruction('물컵을 실제 입 위치로 옮기세요', mouth.actual?'파란 원은 현재 화면에서 인식된 입 위치입니다.':'파란 원은 입 위치 추정 목표입니다.', 'drink'); return; }
    beginHold(); speakOnce('cup_drink_hold'); setInstruction('3단계: 입 위치에서 잠시 멈추세요',`${Math.round(clamp(holdProgress(),0,1)*100)}%`, 'warn'); if(holdProgress()>=1) onSuccess();
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
  if(calMode){ processCalibration(m); return; }
  const type=CONFIG.exercise.taskType;
  if(!target) spawnTaskTarget();
  if(type==='bubble') processBubble(m); else if(type==='cup_drink') processCupDrink(m); else if(type==='hand_bubbles') processHandBubbles(m); else processBubble(m);
  checkStepTimeout();
}
function processCalibration(m){
  const progress=clamp((now()-calStart)/2200,0,1); ui.calFill.style.width=`${Math.round(progress*100)}%`; calSamples.push({pinch:m.pinch,fingertipAvg:m.fingertipAvg,angle:m.angle});
  if(progress>=1){ const avg={pinch:mean(calSamples.map(s=>s.pinch)),fingertipAvg:mean(calSamples.map(s=>s.fingertipAvg)),angle:mean(calSamples.map(s=>s.angle))}; if(calMode==='open') openMetrics=avg; else closeMetrics=avg; calMode=null; calSamples=[]; ui.calFill.style.width='100%'; ui.calStatus.textContent=`편 상태: ${openMetrics?'완료':'미완료'} / 쥔·집은 상태: ${closeMetrics?'완료':'미완료'}`; speakOnce('cal_done',true); setInstruction('보정이 완료되었습니다','훈련 목표로 손을 이동하세요.','ready'); state='waiting_hand'; }
}
function completeGame(){
  if(state==='complete') return;
  state='complete'; stage='complete'; paused=true;
  const totalSec=(now()-gameStartTime)/1000;
  const meanRt=mean(reactionTimes);
  const failCount=failureCount;
  const completeVoice = `축하합니다. 목표 과제를 성공적으로 달성했습니다. 총 ${CONFIG.targetCount}개의 물방울 중 ${successes}개를 터뜨렸습니다. 실패 횟수는 ${failCount}회이고, 평균 성공 시간은 ${meanRt.toFixed(2)}초입니다. 훈련을 종료합니다. 화면의 결과 저장 버튼을 눌러 기록을 저장할 수 있습니다.`;
  setInstruction('훈련을 성공적으로 달성했습니다',`성공 ${successes}회 · 실패 ${failCount}회 · 평균 성공시간 ${meanRt.toFixed(2)}초`, 'ready');
  speakText('complete_summary_'+targetSerial, completeVoice, true);
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
  if(handData&&handData.landmarks){ const lm=handData.landmarks.map(p=>({...p,x:CONFIG.mirrorView?1-p.x:p.x})); drawHand(lm); if(m){ const c=cursorPx(m); ctx.fillStyle=smoothedGesture>=CONFIG.gestureThreshold?'#33d17a':'#ffd166'; ctx.beginPath(); ctx.arc(c.x,c.y,13,0,Math.PI*2); ctx.fill(); ctx.strokeStyle='#fff'; ctx.lineWidth=3; ctx.stroke(); } }
  if(state==='complete'){ ctx.fillStyle='rgba(0,0,0,.58)'; ctx.fillRect(0,0,canvas.width,canvas.height); ctx.fillStyle='#33d17a'; ctx.font='bold 44px sans-serif'; ctx.textAlign='center'; ctx.fillText('훈련 완료',canvas.width/2,canvas.height/2-20); ctx.fillStyle='#fff'; ctx.font='24px sans-serif'; ctx.fillText(`성공 ${successes}/${CONFIG.targetCount} · 실패 ${failureCount} · 평균 ${mean(reactionTimes).toFixed(2)}초`,canvas.width/2,canvas.height/2+25); }
}
function drawGuide(){ ctx.strokeStyle='rgba(255,255,255,.33)'; ctx.lineWidth=2; ctx.setLineDash([8,8]); ctx.beginPath(); ctx.moveTo(canvas.width/2,0); ctx.lineTo(canvas.width/2,canvas.height); ctx.stroke(); ctx.beginPath(); ctx.moveTo(0,canvas.height/2); ctx.lineTo(canvas.width,canvas.height/2); ctx.stroke(); ctx.setLineDash([]); ctx.fillStyle='rgba(87,166,255,.10)'; ctx.fillRect(canvas.width*.12,canvas.height*.10,canvas.width*.76,canvas.height*.80); }
function drawBubble(o){
  if(!o)return;
  const x=o.x, y=o.y, r=o.r;
  ctx.save();
  ctx.shadowColor='rgba(30,160,255,.45)'; ctx.shadowBlur=18;
  const grad=ctx.createRadialGradient(x-r*.28,y-r*.36,r*.06,x,y+r*.10,r*1.18);
  grad.addColorStop(0,'rgba(255,255,255,.98)');
  grad.addColorStop(.18,'rgba(192,238,255,.96)');
  grad.addColorStop(.55,'rgba(70,183,255,.82)');
  grad.addColorStop(1,'rgba(0,93,205,.72)');
  ctx.fillStyle=grad;
  // Real water-drop silhouette: round lower body with pointed top.
  ctx.beginPath();
  ctx.moveTo(x, y-r*1.25);
  ctx.bezierCurveTo(x-r*.78, y-r*.36, x-r*.88, y+r*.20, x-r*.54, y+r*.62);
  ctx.bezierCurveTo(x-r*.18, y+r*1.08, x+r*.18, y+r*1.08, x+r*.54, y+r*.62);
  ctx.bezierCurveTo(x+r*.88, y+r*.20, x+r*.78, y-r*.36, x, y-r*1.25);
  ctx.closePath();
  ctx.fill();
  ctx.shadowBlur=0;
  ctx.strokeStyle='rgba(255,255,255,.86)'; ctx.lineWidth=Math.max(2,r*.045); ctx.stroke();
  // Specular highlights make it read as a water droplet rather than a flat marker.
  ctx.fillStyle='rgba(255,255,255,.90)';
  ctx.beginPath(); ctx.ellipse(x-r*.24,y-r*.28,r*.14,r*.25,-.55,0,Math.PI*2); ctx.fill();
  ctx.fillStyle='rgba(255,255,255,.55)';
  ctx.beginPath(); ctx.arc(x+r*.18,y+r*.25,r*.10,0,Math.PI*2); ctx.fill();
  ctx.restore();
}

function drawAirBubble(o, active=false){
  if(!o || o.popped) return;
  const x=o.x,y=o.y,r=o.r;
  ctx.save();
  const pulse = 1 + Math.sin(o.shimmer||0)*0.025;
  const rr = r*pulse;
  ctx.shadowColor='rgba(80,190,255,.28)'; ctx.shadowBlur=active?18:10;
  const grad=ctx.createRadialGradient(x-rr*.30,y-rr*.34,rr*.06,x,y,rr);
  grad.addColorStop(0,'rgba(255,255,255,.98)');
  grad.addColorStop(.18,'rgba(228,249,255,.88)');
  grad.addColorStop(.55,'rgba(144,219,255,.40)');
  grad.addColorStop(1,'rgba(92,180,255,.14)');
  ctx.fillStyle=grad;
  ctx.beginPath(); ctx.arc(x,y,rr,0,Math.PI*2); ctx.fill();
  ctx.shadowBlur=0;
  ctx.strokeStyle=active?'rgba(255,209,102,.98)':'rgba(220,248,255,.95)'; ctx.lineWidth=active?5:3;
  ctx.beginPath(); ctx.arc(x,y,rr,0,Math.PI*2); ctx.stroke();
  ctx.strokeStyle='rgba(255,255,255,.86)'; ctx.lineWidth=Math.max(2,rr*.04);
  ctx.beginPath(); ctx.arc(x-rr*.18,y-rr*.18,rr*.38,Math.PI*1.05,Math.PI*1.63); ctx.stroke();
  ctx.fillStyle='rgba(255,255,255,.84)';
  ctx.beginPath(); ctx.ellipse(x-rr*.28,y-rr*.34,rr*.11,rr*.17,-.55,0,Math.PI*2); ctx.fill();
  ctx.fillStyle='rgba(255,255,255,.46)';
  ctx.beginPath(); ctx.arc(x+rr*.18,y+rr*.18,rr*.08,0,Math.PI*2); ctx.fill();
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
  ctx.save();
  ctx.shadowColor='rgba(0,0,0,.28)'; ctx.shadowBlur=10; ctx.shadowOffsetY=4;
  // Transparent tapered glass cup.
  const topW=r*1.18, botW=r*.74, h=r*1.36;
  const topY=y-r*.72, botY=y+r*.66;
  const cupPath=[
    {x:x-topW/2,y:topY},{x:x+topW/2,y:topY},
    {x:x+botW/2,y:botY},{x:x-botW/2,y:botY}
  ];
  const glassGrad=ctx.createLinearGradient(x-topW/2,topY,x+topW/2,botY);
  glassGrad.addColorStop(0,'rgba(255,255,255,.40)');
  glassGrad.addColorStop(.35,'rgba(210,240,255,.18)');
  glassGrad.addColorStop(.65,'rgba(130,210,255,.16)');
  glassGrad.addColorStop(1,'rgba(255,255,255,.32)');
  ctx.fillStyle=glassGrad;
  ctx.strokeStyle='rgba(235,250,255,.92)'; ctx.lineWidth=Math.max(3,r*.055);
  roundedPoly(cupPath, r*.10); ctx.fill(); ctx.stroke();
  // Rim ellipse and base.
  ctx.shadowBlur=0;
  ctx.strokeStyle='rgba(255,255,255,.88)'; ctx.lineWidth=Math.max(2,r*.035);
  ctx.beginPath(); ctx.ellipse(x,topY,topW/2,r*.12,0,0,Math.PI*2); ctx.stroke();
  ctx.beginPath(); ctx.ellipse(x,botY,botW/2,r*.08,0,0,Math.PI*2); ctx.stroke();
  if(filled){
    const waterY=y+r*.10;
    const waterH=botY-waterY-r*.03;
    const waterGrad=ctx.createLinearGradient(x,waterY,x,botY);
    waterGrad.addColorStop(0,'rgba(95,219,255,.85)');
    waterGrad.addColorStop(1,'rgba(22,135,255,.65)');
    ctx.save(); roundedPoly(cupPath,r*.08); ctx.clip();
    ctx.fillStyle=waterGrad; ctx.fillRect(x-topW*.46,waterY,topW*.92,waterH);
    ctx.strokeStyle='rgba(230,255,255,.75)'; ctx.lineWidth=2;
    ctx.beginPath(); ctx.ellipse(x,waterY,topW*.38,r*.07,0,0,Math.PI*2); ctx.stroke();
    ctx.restore();
  }
  // Bright vertical highlight.
  ctx.strokeStyle='rgba(255,255,255,.70)'; ctx.lineWidth=Math.max(2,r*.026);
  ctx.beginPath(); ctx.moveTo(x-topW*.28,topY+r*.12); ctx.lineTo(x-botW*.22,botY-r*.12); ctx.stroke();
  ctx.fillStyle='#fff'; ctx.font=`bold ${Math.max(13,Math.round(r*.20))}px sans-serif`; ctx.textAlign='center';
  ctx.fillText(label,x,y+r*1.02);
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
function drawMouth(o){ if(!o)return; ctx.fillStyle=o.actual?'rgba(96,230,255,.24)':'rgba(255,209,102,.20)'; ctx.strokeStyle=o.actual?'rgba(96,230,255,.95)':'rgba(255,209,102,.90)'; ctx.lineWidth=4; ctx.setLineDash(o.actual?[]:[8,6]); ctx.beginPath(); ctx.arc(o.x,o.y,o.r,0,Math.PI*2); ctx.fill(); ctx.stroke(); ctx.setLineDash([]); ctx.fillStyle='#fff'; ctx.font='bold 15px sans-serif'; ctx.textAlign='center'; ctx.fillText(o.actual?'실제 입 위치':'입 위치 추정',o.x,o.y+5); }
function drawTargets(){ if(!target)return; if(target.kind==='bubble') drawBubble(target); if(target.kind==='air_bubbles' && target.bubbles){ for(const b of target.bubbles){ drawAirBubble(b, b.id===target.activeId); } if(target.anchor){ ctx.fillStyle='rgba(255,255,255,.88)'; ctx.font='bold 18px sans-serif'; ctx.textAlign='center'; ctx.fillText(`남은 물방울 ${remainingBubbles()}개`, target.anchor.x, Math.max(26, target.anchor.y-18)); } } if(target.cup) drawCup(target.cup,target.cup.filled,'물컵'); if(target.pitcher) drawPitcher(target.pitcher); if(target.mouth) drawMouth(target.mouth); }
function drawParticles(){ particles=particles.filter(p=>p.life>0); for(const p of particles){ p.x+=p.vx; p.y+=p.vy; p.life--; ctx.fillStyle=`rgba(96,230,255,${p.life/50})`; ctx.beginPath(); ctx.arc(p.x,p.y,4,0,Math.PI*2); ctx.fill(); } }
function drawHand(lm){ const con=[[0,1],[1,2],[2,3],[3,4],[0,5],[5,6],[6,7],[7,8],[5,9],[9,10],[10,11],[11,12],[9,13],[13,14],[14,15],[15,16],[13,17],[17,18],[18,19],[19,20],[0,17]]; ctx.strokeStyle='rgba(51,209,122,.95)'; ctx.fillStyle='#33d17a'; ctx.lineWidth=3; for(const [a,b] of con){ ctx.beginPath(); ctx.moveTo(lm[a].x*canvas.width,lm[a].y*canvas.height); ctx.lineTo(lm[b].x*canvas.width,lm[b].y*canvas.height); ctx.stroke(); } for(let i=0;i<lm.length;i++){ const r=[4,8,12,16,20].includes(i)?6:4; ctx.beginPath(); ctx.arc(lm[i].x*canvas.width,lm[i].y*canvas.height,r,0,Math.PI*2); ctx.fill(); } }
function renderLoop(){
  if(!running)return; animationId=requestAnimationFrame(renderLoop);
  if(paused||!handLandmarker||video.readyState<2){ drawScene(null,null); return; }
  try{
    if(video.currentTime===lastVideoTime)return; lastVideoTime=video.currentTime; const frameTime=performance.now(); const result=handLandmarker.detectForVideo(video,frameTime); const faceResult=faceLandmarker?faceLandmarker.detectForVideo(video,frameTime):null; updateMouthTargetFromFace(faceResult); const hand=chooseHand(result);
    if(!hand){ if(now()-lastHandFoundAt>2500)speakOnce('hand_not_found'); if(['cup_to_mouth','air_hold','hold_gesture'].includes(stage) || ['hold_gesture','do_gesture','air_bubble_hold'].includes(state)){ if(now()-lastHandFoundAt>5000) onFailure('손이 화면에서 사라졌습니다.'); } setInstruction('손이 보이지 않습니다','손 전체가 화면에 들어오도록 조정하세요.','bad'); drawScene(null,null); updateUI(); return; }
    if(hand.wrongHand){ speakOnce('wrong_hand'); setInstruction('선택한 손이 아닙니다','설정한 훈련 손을 카메라 앞에 보여 주세요.','bad'); drawScene(hand,null); return; }
    lastHandFoundAt=now(); const m=handMetrics(hand.landmarks); if(hand.score<CONFIG.minHandConfidence){ speakOnce('low_quality'); setInstruction('손 인식이 불안정합니다','조명, 손 가림, 카메라 각도를 조정하세요.','bad'); }
    processGame(m,hand.handed,hand.score); drawScene(hand,m); updateUI();
  }catch(e){ console.error(e); log(String(e)); }
}
function bindButtons(){
  window.startApp = startApp;
  window.unlockAudio = unlockAudio;
  window.stopApp = stopApp;
  btn.start.onclick = startApp;
  btn.sound.onclick = unlockAudio;
  btn.openCal.onclick = () => startCalibration('open');
  btn.closeCal.onclick = () => startCalibration('close');
  btn.reset.onclick = () => resetGame(true);
  btn.pause.onclick = () => { paused=!paused; btn.pause.textContent=paused?'재개':'일시정지'; speakOnce(paused?'pause':'resume',true); };
  btn.stop.onclick = stopApp;
}
bindButtons();
setInstruction('카메라/모델 시작을 누르세요','버튼을 눌렀을 때 문구가 바뀌면 버튼 입력은 정상입니다. 모델 로딩 오류가 있으면 화면에 표시됩니다.','info');
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
