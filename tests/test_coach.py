from datetime import datetime, timezone

import random

from core.coach import CoachResponder, ToneContext


class FixedRandom(random.Random):
    def choice(self, seq):  # type: ignore[override]
        return seq[0]


def test_coach_responder_generates_morning_message():
    responder = CoachResponder(rng=FixedRandom())
    ctx = ToneContext(
        loot_type="ACHIEVEMENT",
        loot_title="체중 기록",
        boss_name="사업자등록 완료",
        theme_preference="GAME",
        time_of_day="morning",
    )

    message = responder.generate(
        ctx, now=datetime(2025, 1, 1, 8, 0, tzinfo=timezone.utc)
    )

    assert "체중" in message
    assert "보스전" in message
    assert "좋은 아침" in message


def test_coach_responder_handles_recovery():
    responder = CoachResponder(rng=FixedRandom())
    ctx = ToneContext(
        energy_status="NEEDS_POTION",
        challenge_appetite="LOW",
        theme_preference="PROFESSIONAL",
        time_of_day="evening",
    )

    message = responder.generate(
        ctx, now=datetime(2025, 1, 1, 20, 0, tzinfo=timezone.utc)
    )

    assert "회복" in message or "물약" in message
    assert "회복" in message


def test_coach_responder_hybrid_fallback():
    called = {}

    def llm_callback(ctx):
        called['used'] = True
        return 'LLM 응답: 오늘은 어떤 전리품을 남겨볼까요?'

    responder = CoachResponder(rng=FixedRandom(), llm_callback=llm_callback)
    ctx = ToneContext()

    message = responder.generate(ctx, now=datetime(2025, 1, 1, 9, 0, tzinfo=timezone.utc))

    assert called.get('used') is True
    assert '전리품' in message
