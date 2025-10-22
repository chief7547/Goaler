"""Privacy utilities for masking sensitive user-provided text."""

from __future__ import annotations

import re

_SENSITIVE_PATTERNS = [
    re.compile(r"\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b"),  # 이메일
    re.compile(r"\b\d{2,3}-?\d{3,4}-?\d{4}\b"),  # 전화번호
    re.compile(r"\b\d{6}-?\d{7}\b"),  # 주민등록번호 형식
    re.compile(r"\b(?:\d[ -]?){13,16}\b"),  # 카드 번호 유사 패턴
]

_SENSITIVE_KEYWORDS = ["주민등록", "주민번", "신용카드", "계좌번호"]


def sanitize_note(text: str | None) -> str | None:
    if not text:
        return text
    sanitized = text
    for pattern in _SENSITIVE_PATTERNS:
        sanitized = pattern.sub("[민감정보]", sanitized)
    for keyword in _SENSITIVE_KEYWORDS:
        if keyword in sanitized:
            sanitized = sanitized.replace(keyword, "[민감정보]")
    return sanitized


__all__ = ["sanitize_note"]
