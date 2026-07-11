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
    "cup_pour_drink": {
        "label": "가상 물컵에 물 따르고 잡고 마시기",
        "taskType": "pour_drink",
        "gesture": "grasp",
        "targetName": "물병/물컵",
        "description": "물병을 잡아 컵 위로 옮겨 기울여 물을 따른 뒤, 컵을 잡고 입 위치로 가져가면 성공합니다.",
        "clinicalGoal": "잡기, 전완/손목 조절, 목표 지향 이동, 마시기 ADL 순차 과제",
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
    target_count = st.slider("목표 물방울/과제 수", min_value=3, max_value=30, value=level_cfg["targetCount"], step=1)
    hold_ms = st.slider("끝동작 유지 시간(ms)", min_value=200, max_value=2500, value=level_cfg["holdMs"], step=50)
    gesture_threshold = st.slider("손동작 인정 기준", min_value=0.05, max_value=0.95, value=float(level_cfg["gestureThreshold"]), step=0.05)
    target_size_scale = st.slider("물방울/물컵 크기 보정", min_value=0.60, max_value=1.80, value=1.00, step=0.05)
    speed_scale = st.slider("물방울/물컵 속도 보정", min_value=0.00, max_value=2.50, value=1.00, step=0.10)
    st.divider()
    robustness = st.slider("손 떨림 보정/움직임 안정화", min_value=0.0, max_value=1.0, value=0.55, step=0.05)
    min_hand_conf = st.slider("손 인식 최소 신뢰도", min_value=0.20, max_value=0.80, value=0.45, step=0.05)
    use_front_camera = st.checkbox("스마트폰 전면 카메라 우선", value=True)
    mirror_view = st.checkbox("거울 모드로 보기", value=True)
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
    4. 선택한 과제에 따라 물방울, 물컵, 주전자 목표를 수행합니다.  
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
    "gestureThreshold": float(gesture_threshold),
    "targetSizeScale": float(target_size_scale),
    "speedScale": float(speed_scale),
    "robustness": float(robustness),
    "minHandConfidence": float(min_hand_conf),
    "useFrontCamera": bool(use_front_camera),
    "mirrorView": bool(mirror_view),
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
  modeLabel: document.getElementById('modeLabel'), big: document.getElementById('bigInstruction'), sub: document.getElementById('subInstruction'), state: document.getElementById('stateText'), score: document.getElementById('scoreText'), gesture: document.getElementById('gestureText'), hand: document.getElementById('handText'), accuracy: document.getElementById('accuracyText'), rt: document.getElementById('rtText'), log: document.getElementById('logBox'), calStatus: document.getElementById('calStatus'), calFill: document.getElementById('calFill'), downloadArea: document.getElementById('downloadArea')
};
const btn = { start:document.getElementById('btnStart'), sound:document.getElementById('btnSound'), openCal:document.getElementById('btnOpenCal'), closeCal:document.getElementById('btnCloseCal'), reset:document.getElementById('btnReset'), pause:document.getElementById('btnPause'), stop:document.getElementById('btnStop') };

const messages = {
  sound_test:'소리 안내가 활성화되었습니다.', start_camera:'카메라를 시작합니다. 손을 화면 중앙에 보여 주세요.', hand_not_found:'손이 보이지 않습니다. 손 전체가 화면에 들어오도록 조정하세요.', wrong_hand:'선택한 손이 아닙니다. 훈련 손을 다시 확인하세요.', low_quality:'손 인식이 불안정합니다. 조명을 밝게 하고 손 가림을 줄여 주세요.',
  open_cal_start:'손을 최대한 편 상태로 유지하세요.', close_cal_start: CONFIG.exercise.gesture==='pinch' ? '엄지와 검지를 맞댄 상태로 유지하세요.' : '손을 쥐는 상태로 유지하세요.', cal_done:'보정이 완료되었습니다.',
  seek_target:'목표 위치로 손을 가져가세요.', now_gesture: CONFIG.exercise.gesture==='pinch' ? '엄지와 검지를 맞대어 집으세요.' : (CONFIG.exercise.gesture==='open' ? '손을 충분히 펴세요.' : '손을 쥐세요.'), hold_gesture:'끝동작을 잠시 유지하세요.', success:'성공입니다. 다음 목표로 이동하세요.', complete:'훈련이 끝났습니다. 결과를 확인하세요.',
  cup_reach:'물컵으로 손을 가져가세요.', cup_grasp:'물컵을 잡으세요.', cup_to_mouth:'물컵을 입 위치 목표까지 천천히 옮기세요.', cup_drink_hold:'입 위치에서 잠시 멈추세요.',
  pour_reach_pitcher:'물병으로 손을 가져가세요.', pour_grasp_pitcher:'물병을 잡으세요.', pour_move_to_cup:'물병을 컵 위로 옮기세요.', pour_tilt:'손목을 기울여 물을 따르는 자세를 유지하세요.', pour_done:'물이 채워졌습니다. 이제 물컵을 잡으세요.',
  pause:'훈련을 일시정지합니다.', resume:'훈련을 다시 시작합니다.'
};

let handLandmarker=null, stream=null, running=false, paused=false, animationId=null, lastVideoTime=-1;
let audioCtx=null, soundUnlocked=false, lastSpeakKey='', lastSpeakAt=0;
let state='idle', score=0, attempts=0, successes=0, reactionTimes=[], gameStartTime=0;
let target=null, stage='none', holdStart=null, overlapStart=null, reactionStart=null, lastStatusVoice=0;
let openMetrics=null, closeMetrics=null, calMode=null, calSamples=[], calStart=0;
let smoothLandmarks=null, smoothedGesture=0, smoothedCursor=null, lastHandFoundAt=0, neutralTilt=null;
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
  if(key==='success'){beep(740,.08,.08); setTimeout(()=>beep(980,.10,.08),110);} else if(key==='complete'){beep(660,.08,.08); setTimeout(()=>beep(880,.08,.08),110); setTimeout(()=>beep(1100,.12,.08),230);} else if(['wrong_hand','hand_not_found','low_quality'].includes(key)){beep(220,.16,.09); setTimeout(()=>beep(180,.16,.09),190);} else if(['now_gesture','cup_grasp','pour_grasp_pitcher','pour_tilt'].includes(key)){beep(880,.12,.08);} else {beep(600,.08,.05);}
}
function speakOnce(key, force=false){
  const t=now(); if(!force && key===lastSpeakKey && t-lastSpeakAt<2600) return; lastSpeakKey=key; lastSpeakAt=t;
  const text=messages[key]||key; ui.sub.textContent=text;
  if(navigator.vibrate){ if(['success','complete'].includes(key)) navigator.vibrate([70,40,70]); else if(['wrong_hand','hand_not_found','low_quality'].includes(key)) navigator.vibrate([120,60,120]); else navigator.vibrate(45); }
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
  try{ window.speechSynthesis.cancel(); const u=new SpeechSynthesisUtterance(text); u.lang='ko-KR'; u.rate=.92; u.pitch=1.0; u.volume=1.0; u.onerror=()=>toneFor(key); window.speechSynthesis.speak(u); setTimeout(()=>{ if(window.speechSynthesis.speaking===false) toneFor(key); },700); }catch(e){ toneFor(key); }
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
      ui.modeLabel.textContent='모델 로딩 중: GPU';
      handLandmarker = await HandLandmarker.createFromOptions(vision, handOptions('GPU'));
    }catch(gpuErr){
      console.warn('GPU delegate failed. Fallback to CPU.', gpuErr);
      ui.modeLabel.textContent='모델 로딩 중: CPU';
      handLandmarker = await HandLandmarker.createFromOptions(vision, handOptions('CPU'));
    }
    ui.modeLabel.textContent='카메라 권한 요청 중';
    stream = await navigator.mediaDevices.getUserMedia({ video:{ facingMode:CONFIG.useFrontCamera?'user':'environment', width:{ideal:960}, height:{ideal:720}, frameRate:{ideal:24,max:30}}, audio:false });
    video.srcObject=stream; await video.play();
    canvas.width=video.videoWidth||960; canvas.height=video.videoHeight||720;
    running=true; paused=false; resetGame(false); speakOnce('start_camera',true); renderLoop();
  }catch(e){ console.error(e); setInstruction('카메라 또는 모델을 시작할 수 없습니다','HTTPS 접속, 카메라 권한, 브라우저를 확인하세요.','bad'); log(String(e)); }
}
function stopApp(){ running=false; paused=false; if(animationId) cancelAnimationFrame(animationId); if(stream) stream.getTracks().forEach(t=>t.stop()); stream=null; setInstruction('카메라가 정지되었습니다','다시 시작하려면 카메라/모델 시작을 누르세요.','info'); }
function resetGame(announce=true){
  score=0; attempts=0; successes=0; reactionTimes=[]; target=null; stage='none'; holdStart=null; overlapStart=null; reactionStart=null; particles=[]; gameStartTime=now(); state='waiting_hand'; ui.downloadArea.innerHTML=''; neutralTilt=null; updateUI(); spawnTaskTarget(); if(announce) speakOnce(taskStartMessage(),true);
}
function taskStartMessage(){ const t=CONFIG.exercise.taskType; if(t==='cup_drink') return 'cup_reach'; if(t==='pour_drink') return 'pour_reach_pitcher'; return 'seek_target'; }

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
function spawnTaskTarget(){
  const r=targetRadius(); const type=CONFIG.exercise.taskType;
  holdStart=null; overlapStart=null; reactionStart=now();
  if(type==='bubble'){ target=randomTarget(r); target.kind='bubble'; stage='seek'; state='seek_target'; }
  else if(type==='cup_drink'){ target={cup:{x:canvas.width*.25,y:canvas.height*.64,r:r*.82,attached:false}, mouth:{x:canvas.width*.74,y:canvas.height*.25,r:r*.78}}; stage='cup_reach'; state='cup_reach'; }
  else { target={pitcher:{x:canvas.width*.22,y:canvas.height*.62,r:r*.86,attached:false}, cup:{x:canvas.width*.62,y:canvas.height*.62,r:r*.72,filled:false}, mouth:{x:canvas.width*.78,y:canvas.height*.25,r:r*.70}}; stage='pour_reach_pitcher'; state='pour_reach_pitcher'; }
}
function moveTarget(t){ if(!t||!t.vx) return; t.x+=t.vx; t.y+=t.vy; if(t.x<t.r||t.x>canvas.width-t.r) t.vx*=-1; if(t.y<t.r||t.y>canvas.height-t.r) t.vy*=-1; }
function insidePoint(p,obj,scale=1.0){ return Math.hypot(p.x-obj.x,p.y-obj.y) <= obj.r*scale; }
function holdProgress(){ return holdStart ? (now()-holdStart)/CONFIG.holdMs : 0; }
function beginHold(){ if(!holdStart){ holdStart=now(); speakOnce('hold_gesture'); } }
function resetHold(){ holdStart=null; }
function onSuccess(){
  score++; successes++; attempts++; if(reactionStart) reactionTimes.push((now()-reactionStart)/1000); addParticles(); speakOnce('success',true); updateUI();
  if(score>=CONFIG.targetCount){ completeGame(); return; }
  setTimeout(()=>{ if(running&&!paused&&state!=='complete'){ spawnTaskTarget(); speakOnce(taskStartMessage(),true); } }, 850);
}
function addParticles(){ for(let i=0;i<18;i++){ particles.push({x:(target?.x||target?.cup?.x||canvas.width/2), y:(target?.y||target?.cup?.y||canvas.height/2), vx:(Math.random()*2-1)*3, vy:(Math.random()*2-1)*3, life:30+Math.random()*20}); } }

function processBubble(m){
  if(!target) spawnTaskTarget(); moveTarget(target);
  const c=cursorPx(m); const inside=insidePoint(c,target,1.05); const g=smoothedGesture>=CONFIG.gestureThreshold || CONFIG.level===1;
  if(!inside){ resetHold(); if(now()-lastStatusVoice>4500){speakOnce('seek_target'); lastStatusVoice=now();} setInstruction(`${CONFIG.exercise.targetName}에 손을 가져가세요`,'목표 안에 손이 들어가면 다음 안내가 나옵니다.','info'); state='seek_target'; return; }
  if(!g){ resetHold(); speakOnce('now_gesture'); const action=CONFIG.exercise.gesture==='pinch'?'엄지와 검지를 맞대세요':CONFIG.exercise.gesture==='open'?'손을 충분히 펴세요':'손을 쥐세요'; setInstruction(action,'목표 안에서 끝동작을 수행합니다.','action'); state='do_gesture'; return; }
  beginHold(); const hp=holdProgress(); setInstruction('끝동작을 잠시 유지하세요',`${Math.round(clamp(hp,0,1)*100)}%`, 'warn'); state='hold_gesture'; if(hp>=1) onSuccess();
}
function processCupDrink(m){
  const c=cursorPx(m); const cup=target.cup, mouth=target.mouth; const g=smoothedGesture>=CONFIG.gestureThreshold || CONFIG.level===1;
  if(stage==='cup_reach'){
    if(!insidePoint(c,cup,1.08)){ resetHold(); speakOnce('cup_reach'); setInstruction('물컵으로 손을 가져가세요','손바닥 중심이 물컵 안에 들어가도록 이동합니다.','info'); return; }
    if(!g){ resetHold(); speakOnce('cup_grasp'); setInstruction('물컵을 잡으세요','손을 쥔 상태를 유지하면 컵이 손에 붙습니다.','action'); return; }
    beginHold(); setInstruction('물컵을 잡은 상태를 유지하세요',`${Math.round(clamp(holdProgress(),0,1)*100)}%`, 'warn'); if(holdProgress()>=1){ cup.attached=true; stage='cup_to_mouth'; resetHold(); speakOnce('cup_to_mouth',true); }
    return;
  }
  if(stage==='cup_to_mouth'){
    cup.x=c.x; cup.y=c.y;
    if(!insidePoint(c,mouth,.95)){ resetHold(); setInstruction('물컵을 입 위치 목표로 옮기세요','파란 입 위치 영역까지 천천히 이동합니다.','drink'); return; }
    beginHold(); speakOnce('cup_drink_hold'); setInstruction('입 위치에서 잠시 멈추세요',`${Math.round(clamp(holdProgress(),0,1)*100)}%`, 'warn'); if(holdProgress()>=1) onSuccess();
  }
}
function angleDelta(a,b){ let d=a-b; while(d>180)d-=360; while(d<-180)d+=360; return d; }
function processPourDrink(m){
  const c=cursorPx(m); const p=target.pitcher, cup=target.cup, mouth=target.mouth; const g=smoothedGesture>=CONFIG.gestureThreshold || CONFIG.level===1;
  if(stage==='pour_reach_pitcher'){
    if(!insidePoint(c,p,1.08)){ resetHold(); speakOnce('pour_reach_pitcher'); setInstruction('주전자로 손을 가져가세요','손바닥 중심이 주전자 손잡이 영역에 들어가도록 이동합니다.','info'); return; }
    if(!g){ resetHold(); speakOnce('pour_grasp_pitcher'); setInstruction('주전자를 잡으세요','손을 쥐어 주전자를 잡습니다.','action'); return; }
    beginHold(); setInstruction('물병을 잡은 상태를 유지하세요',`${Math.round(clamp(holdProgress(),0,1)*100)}%`, 'warn'); if(holdProgress()>=1){ p.attached=true; stage='pour_move_to_cup'; neutralTilt=m.angle; resetHold(); speakOnce('pour_move_to_cup',true); }
    return;
  }
  if(stage==='pour_move_to_cup'){
    p.x=c.x; p.y=c.y;
    if(!insidePoint(c,cup,1.15)){ resetHold(); setInstruction('물병을 컵 위로 옮기세요','컵 위 목표 영역까지 이동합니다.','drink'); return; }
    const tilt=Math.abs(angleDelta(m.angle, neutralTilt||m.angle));
    if(tilt < CONFIG.levelConfig.tiltDeg){ resetHold(); speakOnce('pour_tilt'); setInstruction('손목을 기울여 물을 따르세요',`기울임 ${tilt.toFixed(0)}° / 목표 ${CONFIG.levelConfig.tiltDeg}°`, 'action'); return; }
    beginHold(); setInstruction('물을 따르는 자세를 유지하세요',`${Math.round(clamp(holdProgress(),0,1)*100)}%`, 'warn'); if(holdProgress()>=1){ cup.filled=true; p.attached=false; stage='cup_reach'; resetHold(); speakOnce('pour_done',true); }
    return;
  }
  if(stage==='cup_reach'){
    if(!insidePoint(c,cup,1.08)){ resetHold(); setInstruction('물이 담긴 컵으로 손을 가져가세요','컵을 잡기 위해 손을 컵으로 이동합니다.','info'); return; }
    if(!g){ resetHold(); speakOnce('cup_grasp'); setInstruction('물이 담긴 컵을 잡으세요','손을 쥔 상태를 유지합니다.','action'); return; }
    beginHold(); setInstruction('컵을 잡은 상태를 유지하세요',`${Math.round(clamp(holdProgress(),0,1)*100)}%`, 'warn'); if(holdProgress()>=1){ cup.attached=true; stage='cup_to_mouth'; resetHold(); speakOnce('cup_to_mouth',true); }
    return;
  }
  if(stage==='cup_to_mouth'){
    cup.x=c.x; cup.y=c.y;
    if(!insidePoint(c,mouth,.95)){ resetHold(); setInstruction('물컵을 입 위치 목표로 옮기세요','파란 입 위치 영역까지 천천히 이동합니다.','drink'); return; }
    beginHold(); speakOnce('cup_drink_hold'); setInstruction('입 위치에서 잠시 멈추세요',`${Math.round(clamp(holdProgress(),0,1)*100)}%`, 'warn'); if(holdProgress()>=1) onSuccess();
  }
}
function processGame(m,handed,handScore){
  ui.hand.textContent=`${handed} (${Math.round(100*handScore)}%)`;
  updateGestureDisplay(m);
  if(calMode){ processCalibration(m); return; }
  const type=CONFIG.exercise.taskType;
  if(!target) spawnTaskTarget();
  if(type==='bubble') processBubble(m); else if(type==='cup_drink') processCupDrink(m); else processPourDrink(m);
}
function processCalibration(m){
  const progress=clamp((now()-calStart)/2200,0,1); ui.calFill.style.width=`${Math.round(progress*100)}%`; calSamples.push({pinch:m.pinch,fingertipAvg:m.fingertipAvg,angle:m.angle});
  if(progress>=1){ const avg={pinch:mean(calSamples.map(s=>s.pinch)),fingertipAvg:mean(calSamples.map(s=>s.fingertipAvg)),angle:mean(calSamples.map(s=>s.angle))}; if(calMode==='open') openMetrics=avg; else closeMetrics=avg; calMode=null; calSamples=[]; ui.calFill.style.width='100%'; ui.calStatus.textContent=`편 상태: ${openMetrics?'완료':'미완료'} / 쥔·집은 상태: ${closeMetrics?'완료':'미완료'}`; speakOnce('cal_done',true); setInstruction('보정이 완료되었습니다','훈련 목표로 손을 이동하세요.','ready'); state='waiting_hand'; }
}
function completeGame(){ state='complete'; speakOnce('complete',true); setInstruction('훈련이 끝났습니다','결과를 확인하고 필요하면 훈련 새로 시작을 누르세요.','ready'); const totalSec=(now()-gameStartTime)/1000; const meanRt=mean(reactionTimes); const result={date:new Date().toISOString(), exercise:CONFIG.exercise.label, hand:CONFIG.affectedHand, level:CONFIG.level, targetCount:CONFIG.targetCount, successCount:successes, totalSeconds:Number(totalSec.toFixed(1)), meanReactionTimeSeconds:Number(meanRt.toFixed(2)), holdMs:CONFIG.holdMs, gestureThreshold:CONFIG.gestureThreshold, note:'단일 웹캠 기반 교육/피드백용 손 기능 가상훈련 결과입니다. 임상 진단용으로 사용하려면 별도 검증이 필요합니다.'}; const text=`손 기능 재활 가상훈련 결과\n측정일시: ${result.date}\n훈련과제: ${result.exercise}\n훈련 손: ${result.hand}\n난이도: ${result.level}\n성공: ${result.successCount}/${result.targetCount}\n총 소요시간: ${result.totalSeconds}초\n평균 반응시간: ${result.meanReactionTimeSeconds}초\n끝동작 유지 시간: ${result.holdMs}ms\n손동작 인정 기준: ${result.gestureThreshold}\n주의: ${result.note}\n`; const blob=new Blob([text],{type:'text/plain;charset=utf-8'}); const url=URL.createObjectURL(blob); ui.downloadArea.innerHTML=`<a class="download" download="hand_rehab_result.txt" href="${url}">결과 TXT 다운로드</a>`; updateUI(); }
function updateUI(){ ui.state.textContent=state; ui.score.textContent=`${score}/${CONFIG.targetCount}`; const acc=attempts?successes/attempts*100:(successes?100:0); ui.accuracy.textContent=attempts?`${acc.toFixed(0)}%`:'-'; const rt=mean(reactionTimes); ui.rt.textContent=rt?`${rt.toFixed(2)}초`:'-'; }
function drawScene(handData,m){
  ctx.clearRect(0,0,canvas.width,canvas.height);
  ctx.save(); if(CONFIG.mirrorView){ctx.translate(canvas.width,0);ctx.scale(-1,1);} ctx.drawImage(video,0,0,canvas.width,canvas.height); ctx.restore();
  ctx.fillStyle='rgba(0,0,0,.16)'; ctx.fillRect(0,0,canvas.width,canvas.height);
  drawGuide(); drawTargets(); drawParticles();
  if(handData&&handData.landmarks){ const lm=handData.landmarks.map(p=>({...p,x:CONFIG.mirrorView?1-p.x:p.x})); drawHand(lm); if(m){ const c=cursorPx(m); ctx.fillStyle=smoothedGesture>=CONFIG.gestureThreshold?'#33d17a':'#ffd166'; ctx.beginPath(); ctx.arc(c.x,c.y,13,0,Math.PI*2); ctx.fill(); ctx.strokeStyle='#fff'; ctx.lineWidth=3; ctx.stroke(); } }
  if(state==='complete'){ ctx.fillStyle='rgba(0,0,0,.58)'; ctx.fillRect(0,0,canvas.width,canvas.height); ctx.fillStyle='#33d17a'; ctx.font='bold 44px sans-serif'; ctx.textAlign='center'; ctx.fillText('훈련 완료',canvas.width/2,canvas.height/2-20); ctx.fillStyle='#fff'; ctx.font='24px sans-serif'; ctx.fillText(`성공 ${successes}/${CONFIG.targetCount}`,canvas.width/2,canvas.height/2+25); }
}
function drawGuide(){ ctx.strokeStyle='rgba(255,255,255,.33)'; ctx.lineWidth=2; ctx.setLineDash([8,8]); ctx.beginPath(); ctx.moveTo(canvas.width/2,0); ctx.lineTo(canvas.width/2,canvas.height); ctx.stroke(); ctx.beginPath(); ctx.moveTo(0,canvas.height/2); ctx.lineTo(canvas.width,canvas.height/2); ctx.stroke(); ctx.setLineDash([]); ctx.fillStyle='rgba(87,166,255,.10)'; ctx.fillRect(canvas.width*.12,canvas.height*.10,canvas.width*.76,canvas.height*.80); }
function drawBubble(o){
  if(!o)return;
  // 실제 물방울처럼 보이도록 원형 대신 위가 좁고 아래가 둥근 물방울 벡터 형태로 표현
  const r=o.r, x=o.x, y=o.y;
  ctx.save();
  ctx.shadowColor='rgba(50,180,255,.35)';
  ctx.shadowBlur=14;
  const grad=ctx.createRadialGradient(x-r*.28,y-r*.42,r*.08,x,y,r*1.10);
  grad.addColorStop(0,'rgba(255,255,255,.98)');
  grad.addColorStop(.22,'rgba(167,229,255,.94)');
  grad.addColorStop(.62,'rgba(59,167,255,.78)');
  grad.addColorStop(1,'rgba(0,96,210,.58)');
  ctx.fillStyle=grad;
  ctx.beginPath();
  ctx.moveTo(x, y-r*1.12);
  ctx.bezierCurveTo(x-r*.72, y-r*.20, x-r*.84, y+r*.42, x, y+r*.86);
  ctx.bezierCurveTo(x+r*.84, y+r*.42, x+r*.72, y-r*.20, x, y-r*1.12);
  ctx.closePath();
  ctx.fill();
  ctx.lineWidth=Math.max(2,r*.045);
  ctx.strokeStyle='rgba(230,250,255,.92)';
  ctx.stroke();
  // 하이라이트
  ctx.shadowBlur=0;
  ctx.fillStyle='rgba(255,255,255,.78)';
  ctx.beginPath();
  ctx.ellipse(x-r*.27,y-r*.35,r*.16,r*.29,-0.45,0,Math.PI*2);
  ctx.fill();
  ctx.fillStyle='rgba(255,255,255,.42)';
  ctx.beginPath();
  ctx.ellipse(x+r*.20,y+r*.18,r*.25,r*.12,0.35,0,Math.PI*2);
  ctx.fill();
  ctx.restore();
}
function drawCup(o,filled=false,label='물컵'){
  if(!o)return;
  const x=o.x, y=o.y, r=o.r;
  ctx.save();
  ctx.shadowColor='rgba(0,0,0,.35)'; ctx.shadowBlur=10; ctx.shadowOffsetY=4;
  // 컵 외곽: 실제 유리컵처럼 위가 넓고 아래가 좁은 사다리꼴
  const topW=r*1.18, botW=r*.72, h=r*1.42;
  const topY=y-h*.55, botY=y+h*.52;
  const glassGrad=ctx.createLinearGradient(x-topW/2,topY,x+topW/2,botY);
  glassGrad.addColorStop(0,'rgba(255,255,255,.40)');
  glassGrad.addColorStop(.35,'rgba(210,240,255,.18)');
  glassGrad.addColorStop(1,'rgba(255,255,255,.28)');
  ctx.fillStyle=glassGrad;
  ctx.strokeStyle='rgba(240,250,255,.94)';
  ctx.lineWidth=Math.max(3,r*.045);
  ctx.beginPath();
  ctx.moveTo(x-topW/2, topY);
  ctx.lineTo(x-botW/2, botY);
  ctx.quadraticCurveTo(x, botY+r*.10, x+botW/2, botY);
  ctx.lineTo(x+topW/2, topY);
  ctx.quadraticCurveTo(x, topY-r*.08, x-topW/2, topY);
  ctx.closePath();
  ctx.fill(); ctx.stroke();
  // 컵 입구 타원
  ctx.fillStyle='rgba(255,255,255,.24)';
  ctx.beginPath(); ctx.ellipse(x,topY,topW/2,r*.13,0,0,Math.PI*2); ctx.fill(); ctx.stroke();
  // 물
  if(filled){
    const waterY=y+h*.05;
    const waterGrad=ctx.createLinearGradient(x,waterY,x,botY);
    waterGrad.addColorStop(0,'rgba(95,210,255,.76)');
    waterGrad.addColorStop(1,'rgba(0,120,230,.72)');
    ctx.fillStyle=waterGrad;
    ctx.beginPath();
    ctx.moveTo(x-topW*.39, waterY);
    ctx.quadraticCurveTo(x,waterY-r*.05,x+topW*.39,waterY);
    ctx.lineTo(x+botW*.42,botY-r*.08);
    ctx.quadraticCurveTo(x,botY+r*.02,x-botW*.42,botY-r*.08);
    ctx.closePath();
    ctx.fill();
    ctx.strokeStyle='rgba(180,240,255,.65)'; ctx.lineWidth=2;
    ctx.beginPath(); ctx.ellipse(x,waterY,topW*.39,r*.08,0,0,Math.PI*2); ctx.stroke();
  }
  // 유리 하이라이트
  ctx.strokeStyle='rgba(255,255,255,.65)'; ctx.lineWidth=2;
  ctx.beginPath(); ctx.moveTo(x-topW*.25,topY+r*.18); ctx.lineTo(x-botW*.16,botY-r*.18); ctx.stroke();
  ctx.beginPath(); ctx.moveTo(x+topW*.18,topY+r*.24); ctx.lineTo(x+botW*.12,botY-r*.25); ctx.stroke();
  ctx.shadowBlur=0; ctx.fillStyle='#fff'; ctx.font=`bold ${Math.max(13,r*.18)}px sans-serif`; ctx.textAlign='center';
  ctx.fillText(label,x,y+r*1.02);
  ctx.restore();
}
function drawPitcher(o){
  if(!o)return;
  // 실제 물병 모양: 캡, 목, 몸통, 라벨, 물의 양을 표현
  const x=o.x, y=o.y, r=o.r;
  const tilt=o.attached ? -0.28 : 0;
  ctx.save();
  ctx.translate(x,y); ctx.rotate(tilt);
  ctx.shadowColor='rgba(0,0,0,.35)'; ctx.shadowBlur=10; ctx.shadowOffsetY=4;
  // 물병 몸통
  const w=r*.92, h=r*1.70;
  const bodyY=-h*.18;
  const bottleGrad=ctx.createLinearGradient(-w/2,bodyY-h/2,w/2,bodyY+h/2);
  bottleGrad.addColorStop(0,'rgba(255,255,255,.42)');
  bottleGrad.addColorStop(.42,'rgba(170,220,255,.20)');
  bottleGrad.addColorStop(1,'rgba(255,255,255,.30)');
  ctx.fillStyle=bottleGrad;
  ctx.strokeStyle='rgba(235,250,255,.92)';
  ctx.lineWidth=Math.max(3,r*.045);
  ctx.beginPath();
  ctx.roundRect(-w/2, bodyY-h*.34, w, h*.98, r*.18);
  ctx.fill(); ctx.stroke();
  // 목
  ctx.fillStyle='rgba(230,250,255,.30)';
  ctx.beginPath(); ctx.roundRect(-w*.20, bodyY-h*.60, w*.40, h*.34, r*.09); ctx.fill(); ctx.stroke();
  // 캡
  ctx.fillStyle='rgba(50,130,255,.85)'; ctx.strokeStyle='rgba(190,225,255,.95)';
  ctx.beginPath(); ctx.roundRect(-w*.25, bodyY-h*.73, w*.50, h*.14, r*.05); ctx.fill(); ctx.stroke();
  // 내부 물
  ctx.fillStyle='rgba(75,190,255,.58)';
  ctx.beginPath(); ctx.roundRect(-w*.40, bodyY+h*.10, w*.80, h*.42, r*.12); ctx.fill();
  // 라벨
  ctx.fillStyle='rgba(255,255,255,.82)'; ctx.beginPath(); ctx.roundRect(-w*.45, bodyY-h*.02, w*.90, h*.23, r*.08); ctx.fill();
  ctx.fillStyle='#1263b0'; ctx.font=`bold ${Math.max(12,r*.16)}px sans-serif`; ctx.textAlign='center'; ctx.fillText('WATER',0,bodyY+h*.125);
  // 하이라이트
  ctx.strokeStyle='rgba(255,255,255,.62)'; ctx.lineWidth=2; ctx.beginPath(); ctx.moveTo(-w*.28,bodyY-h*.25); ctx.lineTo(-w*.28,bodyY+h*.42); ctx.stroke();
  // 따르는 물줄기: 컵 위로 옮긴 뒤 기울이는 단계에서 시각화
  if(o.attached){
    ctx.strokeStyle='rgba(104,220,255,.75)'; ctx.lineWidth=Math.max(3,r*.055); ctx.setLineDash([8,8]);
    ctx.beginPath(); ctx.moveTo(w*.45,bodyY-h*.48); ctx.quadraticCurveTo(w*.85,bodyY-h*.10,w*.72,bodyY+h*.28); ctx.stroke(); ctx.setLineDash([]);
  }
  ctx.shadowBlur=0; ctx.fillStyle='#fff'; ctx.font=`bold ${Math.max(13,r*.17)}px sans-serif`; ctx.textAlign='center';
  ctx.fillText('물병',0,r*1.13);
  ctx.restore();
}
function drawMouth(o){
  if(!o)return;
  const x=o.x,y=o.y,r=o.r;
  ctx.save();
  ctx.fillStyle='rgba(96,230,255,.18)'; ctx.strokeStyle='rgba(96,230,255,.92)'; ctx.lineWidth=4;
  ctx.beginPath(); ctx.arc(x,y,r,0,Math.PI*2); ctx.fill(); ctx.stroke();
  // 얼굴/입 목표 아이콘
  ctx.fillStyle='rgba(255,255,255,.86)';
  ctx.beginPath(); ctx.arc(x,y-r*.20,r*.28,0,Math.PI*2); ctx.fill();
  ctx.strokeStyle='rgba(255,90,106,.95)'; ctx.lineWidth=3;
  ctx.beginPath(); ctx.arc(x,y+r*.13,r*.28,0.15*Math.PI,0.85*Math.PI); ctx.stroke();
  ctx.fillStyle='#fff'; ctx.font=`bold ${Math.max(13,r*.17)}px sans-serif`; ctx.textAlign='center'; ctx.fillText('입 위치',x,y+r*1.02);
  ctx.restore();
}
function drawTargets(){ if(!target)return; if(target.kind==='bubble') drawBubble(target); if(target.cup) drawCup(target.cup,target.cup.filled,'물컵'); if(target.pitcher) drawPitcher(target.pitcher); if(target.mouth) drawMouth(target.mouth); }
function drawParticles(){ particles=particles.filter(p=>p.life>0); for(const p of particles){ p.x+=p.vx; p.y+=p.vy; p.life--; ctx.fillStyle=`rgba(96,230,255,${p.life/50})`; ctx.beginPath(); ctx.arc(p.x,p.y,4,0,Math.PI*2); ctx.fill(); } }
function drawHand(lm){ const con=[[0,1],[1,2],[2,3],[3,4],[0,5],[5,6],[6,7],[7,8],[5,9],[9,10],[10,11],[11,12],[9,13],[13,14],[14,15],[15,16],[13,17],[17,18],[18,19],[19,20],[0,17]]; ctx.strokeStyle='rgba(51,209,122,.95)'; ctx.fillStyle='#33d17a'; ctx.lineWidth=3; for(const [a,b] of con){ ctx.beginPath(); ctx.moveTo(lm[a].x*canvas.width,lm[a].y*canvas.height); ctx.lineTo(lm[b].x*canvas.width,lm[b].y*canvas.height); ctx.stroke(); } for(let i=0;i<lm.length;i++){ const r=[4,8,12,16,20].includes(i)?6:4; ctx.beginPath(); ctx.arc(lm[i].x*canvas.width,lm[i].y*canvas.height,r,0,Math.PI*2); ctx.fill(); } }
function renderLoop(){
  if(!running)return; animationId=requestAnimationFrame(renderLoop);
  if(paused||!handLandmarker||video.readyState<2){ drawScene(null,null); return; }
  try{
    if(video.currentTime===lastVideoTime)return; lastVideoTime=video.currentTime; const result=handLandmarker.detectForVideo(video,performance.now()); const hand=chooseHand(result);
    if(!hand){ if(now()-lastHandFoundAt>2500)speakOnce('hand_not_found'); setInstruction('손이 보이지 않습니다','손 전체가 화면에 들어오도록 조정하세요.','bad'); drawScene(null,null); updateUI(); return; }
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
