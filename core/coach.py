"""Utilities for generating coach responses based on tone guides."""

from __future__ import annotations

import random
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional


@dataclass
class ToneContext:
    """Snapshot of data that influences the coach response tone."""

    challenge_appetite: str = "MEDIUM"
    energy_status: Optional[str] = None
    loot_type: Optional[str] = None
    boss_name: Optional[str] = None
    stage_label: Optional[str] = None
    theme_preference: str = "GAME"
    time_of_day: Optional[str] = None  # "morning" | "afternoon" | "evening"
    loot_title: Optional[str] = None
    next_progress: Optional[str] = None


_ACK_TEMPLATES: Dict[str, List[str]] = {
    "default": ["좋아요!", "알겠습니다.", "훌륭해요!"],
    "HIGH": ["모험을 떠나볼까요!", "전투 준비 완료!"],
    "LOW": ["천천히 가볼게요.", "안정적으로 이어가요."],
    "NEEDS_POTION": ["잠깐 숨 고를게요.", "회복부터 챙길게요."],
}

_LOOT_TEMPLATES: Dict[str, List[str]] = {
    "ACHIEVEMENT": [
        "전리품 **{loot}** 획득! 다음 단계가 한층 가까워졌어요.",
        "오늘의 성과 **{loot}** 덕분에 보스전 준비가 {progress}까지 왔습니다.",
        "대단해요! {boss}를 향한 공격이 적중했어요.",
    ],
    "INSIGHT": [
        "방금 깨달은 **{loot}**는 다음 주 전략에 큰 힘이 될 거예요.",
        "좋은 통찰입니다. 내일은 이 배움을 실전에 적용해볼까요?",
        "이런 생각을 남겨주셔서 감사해요. 전리품 덱에 저장해 두었습니다.",
    ],
    "EMOTION": [
        "지금 느끼는 감정이 자연스러워요. 오늘은 마음을 다독이는 루틴을 함께 해볼까요?",
        "그 마음을 기억하고 전리품으로 남겨둘게요. 필요하면 잠시 쉬어가도 괜찮아요.",
        "감정을 기록해 주셔서 고마워요. 제가 든든한 지원이 되어드릴게요.",
    ],
}

_RECOVERY_TEMPLATES: Dict[str, str] = {
    "Warning": "사소한 휴식이 큰 힘이 됩니다. 10분간 회복 루틴을 해볼까요?",
    "Critical": "연속으로 힘듦을 느끼셨어요. 포션 의식을 준비했습니다. 가볍게 따라가 볼까요?",
    "Emergency": "포션 의식이 발동했습니다. 오늘은 반드시 회복 루틴을 따라가 전리품을 지켜요.",
}

_TIME_TONE: Dict[str, str] = {
    "morning": "좋은 아침이에요!",
    "afternoon": "점검해 볼까요?",
    "evening": "오늘도 수고 많았어요.",
}

_THEME_TERMS = {
    "GAME": {
        "boss": "보스전",
        "quest": "퀘스트",
        "loot": "전리품",
        "recovery": "물약",
    },
    "PROFESSIONAL": {
        "boss": "핵심 마일스톤",
        "quest": "실행 계획",
        "loot": "성과/인사이트",
        "recovery": "재충전",
    },
}


def _pick(items: List[str]) -> str:
    return random.choice(items)


def _current_time_slot(now: Optional[datetime]) -> str:
    if now is None:
        now = datetime.now()
    hour = now.hour
    if hour < 12:
        return "morning"
    if hour < 18:
        return "afternoon"
    return "evening"


class CoachResponder:
    """Utility to generate tone-aware responses using template guidance."""

    def __init__(self, *, rng: Optional[random.Random] = None):
        self._rng = rng or random.Random()

    def _choose_ack(self, ctx: ToneContext) -> str:
        if ctx.energy_status == "NEEDS_POTION":
            pool = _ACK_TEMPLATES.get("NEEDS_POTION", _ACK_TEMPLATES["default"])
        else:
            pool = _ACK_TEMPLATES.get(ctx.challenge_appetite, _ACK_TEMPLATES["default"])
        return self._rng.choice(pool)

    def _loot_message(self, ctx: ToneContext, terms: dict) -> Optional[str]:
        if not ctx.loot_type:
            return None
        templates = _LOOT_TEMPLATES.get(ctx.loot_type)
        if not templates:
            return None
        template = self._rng.choice(templates)
        return template.format(
            loot=ctx.loot_title or "오늘의 기록",
            progress=ctx.next_progress or "한 단계",
            boss=ctx.boss_name or terms["boss"],
        )

    def _recovery_message(self, ctx: ToneContext) -> Optional[str]:
        if ctx.energy_status == "NEEDS_POTION":
            return _RECOVERY_TEMPLATES["Warning"]
        if ctx.energy_status == "KEEPING_PACE":
            return None
        if ctx.energy_status == "READY_FOR_BOSS":
            return None
        return None

    def generate(self, ctx: ToneContext, *, now: Optional[datetime] = None) -> str:
        terms = _THEME_TERMS.get(ctx.theme_preference, _THEME_TERMS["GAME"])

        slot = ctx.time_of_day or _current_time_slot(now)
        header = _TIME_TONE.get(slot, _TIME_TONE["morning"])
        ack = self._choose_ack(ctx)

        sections = [ack, header]

        loot_msg = self._loot_message(ctx, terms)
        if loot_msg:
            sections.append(loot_msg)

        recovery_msg = self._recovery_message(ctx)
        if recovery_msg:
            sections.append(recovery_msg)

        if ctx.boss_name and ctx.energy_status != "NEEDS_POTION":
            sections.append(
                f"오늘은 {terms['boss']} '{ctx.boss_name}' 대비로 어떤 {terms['quest']}을 진행해볼까요?"
            )

        return " ".join(section for section in sections if section)


__all__ = ["CoachResponder", "ToneContext"]
