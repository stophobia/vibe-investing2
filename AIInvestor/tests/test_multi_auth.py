"""Multi-auth (Telegram + Google + Guest) helper 검증."""

from __future__ import annotations

import pytest


class TestGuestIdValidation:
    def test_valid_uuid(self) -> None:
        # function_app 에서 _is_valid_guest_id import
        import os
        os.environ.setdefault("TELEGRAM_BOT_TOKEN", "x")
        os.environ.setdefault("DEEPSEEK_API_KEY", "x")
        from function_app import _is_valid_guest_id
        # crypto.randomUUID() 형식
        assert _is_valid_guest_id("550e8400-e29b-41d4-a716-446655440000") is True

    def test_uppercase_normalized(self) -> None:
        import os
        os.environ.setdefault("TELEGRAM_BOT_TOKEN", "x")
        os.environ.setdefault("DEEPSEEK_API_KEY", "x")
        from function_app import _is_valid_guest_id
        # 검증 함수 자체는 소문자만 매치, 호출부에서 .lower()
        assert _is_valid_guest_id("550e8400-e29b-41d4-a716-446655440000".lower())

    def test_invalid_format_rejected(self) -> None:
        import os
        os.environ.setdefault("TELEGRAM_BOT_TOKEN", "x")
        os.environ.setdefault("DEEPSEEK_API_KEY", "x")
        from function_app import _is_valid_guest_id
        assert _is_valid_guest_id("not-a-uuid") is False
        assert _is_valid_guest_id("") is False
        assert _is_valid_guest_id("550e8400e29b41d4a716446655440000") is False  # no dashes
        # 공격 케이스
        assert _is_valid_guest_id("../../../etc/passwd") is False
        assert _is_valid_guest_id("'; DROP TABLE users; --") is False

    def test_wrong_length_rejected(self) -> None:
        import os
        os.environ.setdefault("TELEGRAM_BOT_TOKEN", "x")
        os.environ.setdefault("DEEPSEEK_API_KEY", "x")
        from function_app import _is_valid_guest_id
        # 너무 짧음
        assert _is_valid_guest_id("550e-e29b-41d4-a716-446") is False
        # 너무 김
        assert _is_valid_guest_id("550e8400-e29b-41d4-a716-446655440000-extra") is False


class TestGoogleVerifierShortCircuits:
    """실제 Google 호출 X — 환경변수 부재 시 None 반환만 확인."""

    def test_returns_none_when_no_env(self, monkeypatch) -> None:
        import asyncio
        import os
        os.environ.setdefault("TELEGRAM_BOT_TOKEN", "x")
        os.environ.setdefault("DEEPSEEK_API_KEY", "x")
        monkeypatch.delenv("GOOGLE_OAUTH_CLIENT_ID", raising=False)
        from function_app import _verify_google_id_token
        result = asyncio.run(_verify_google_id_token("any-token"))
        assert result is None

    def test_returns_none_when_empty_token(self, monkeypatch) -> None:
        import asyncio
        import os
        os.environ.setdefault("TELEGRAM_BOT_TOKEN", "x")
        os.environ.setdefault("DEEPSEEK_API_KEY", "x")
        monkeypatch.setenv("GOOGLE_OAUTH_CLIENT_ID", "x.apps.googleusercontent.com")
        from function_app import _verify_google_id_token
        result = asyncio.run(_verify_google_id_token(""))
        assert result is None
