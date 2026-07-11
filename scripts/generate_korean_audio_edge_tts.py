"""Generate optional Korean MP3 prompts with edge-tts.

Usage:
    python -m pip install edge-tts
    python scripts/generate_korean_audio_edge_tts.py

Generated files are saved to assets/audio/.
"""
from __future__ import annotations

import asyncio
from pathlib import Path

import edge_tts

ROOT = Path(__file__).resolve().parents[1]
AUDIO_DIR = ROOT / "assets" / "audio"
AUDIO_DIR.mkdir(parents=True, exist_ok=True)

VOICE = "ko-KR-SunHiNeural"
PROMPTS = {
    "sound_test": "소리 안내가 활성화되었습니다.",
    "start_camera": "카메라를 시작합니다. 손을 화면 중앙에 보여 주세요.",
    "hand_not_found": "손이 보이지 않습니다. 손 전체가 화면에 들어오도록 조정하세요.",
    "wrong_hand": "선택한 손이 아닙니다. 훈련 손을 다시 확인하세요.",
    "low_quality": "손 인식이 불안정합니다. 조명을 밝게 하고 손 가림을 줄여 주세요.",
    "open_cal_start": "손을 최대한 편 상태로 유지하세요.",
    "close_cal_start": "손을 쥐거나 엄지와 검지를 맞댄 상태로 유지하세요.",
    "cal_done": "보정이 완료되었습니다.",
    "seek_target": "목표 위치로 손을 가져가세요.",
    "now_gesture": "끝동작을 수행하세요.",
    "hold_gesture": "끝동작을 잠시 유지하세요.",
    "success": "성공입니다. 다음 목표로 이동하세요.",
    "complete": "훈련이 끝났습니다. 결과를 확인하세요.",
    "cup_reach": "물컵으로 손을 가져가세요.",
    "cup_grasp": "물컵을 잡으세요.",
    "cup_to_mouth": "물컵을 입 위치 목표까지 천천히 옮기세요.",
    "cup_drink_hold": "입 위치에서 잠시 멈추세요.",
    "pour_reach_pitcher": "주전자로 손을 가져가세요.",
    "pour_grasp_pitcher": "주전자를 잡으세요.",
    "pour_move_to_cup": "주전자를 컵 위로 옮기세요.",
    "pour_tilt": "손목을 기울여 물을 따르는 자세를 유지하세요.",
    "pour_done": "물이 채워졌습니다. 이제 물컵을 잡으세요.",
    "pause": "훈련을 일시정지합니다.",
    "resume": "훈련을 다시 시작합니다.",
}

async def main() -> None:
    for key, text in PROMPTS.items():
        out = AUDIO_DIR / f"{key}.mp3"
        print("Generating", out)
        communicate = edge_tts.Communicate(text=text, voice=VOICE, rate="-5%")
        await communicate.save(str(out))

if __name__ == "__main__":
    asyncio.run(main())
