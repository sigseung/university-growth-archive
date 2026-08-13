"""
tests/test_ai_content_service.py

실제 OpenAI API를 호출하지 않고, AIClient.complete를 가짜 응답으로 바꿔치기해서
"AI 응답을 어떻게 처리하는지"의 로직만 검증합니다.
    - 정상 JSON 응답 파싱
    - 마크다운 코드블록으로 감싼 응답도 파싱
    - 잘못된 형식의 응답이면 ValueError
    - API 키가 없으면 AIConfigError
"""

import json
from datetime import date
from unittest.mock import patch

import pytest

from models.activity import ActivityType
from services.activity_service import ActivityService
from services.ai_content_service import AIContentService
from ai.ai_client import AIClient, AIConfigError


def _make_activity(session):
    return ActivityService(session).create_activity(
        title="AI 세미나", activity_type=ActivityType.SEMINAR, date_start=date(2026, 1, 1),
        purpose="목적", content="내용",
    )


def test_ai_client_raises_config_error_without_api_key(session, monkeypatch):
    # 환경변수도, 저장된 키도 없는 상태를 보장합니다.
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    import utils.settings_store as settings_store
    monkeypatch.setattr(settings_store, "get_setting", lambda key, default=None: None)

    with pytest.raises(AIConfigError):
        AIClient().complete("system", "user")


def test_generate_reflection_parses_valid_json(session):
    activity = _make_activity(session)
    fake_response = json.dumps({"learned": "느낀 점", "next_action": "다음 행동"}, ensure_ascii=False)

    with patch("ai.ai_client.AIClient.complete", return_value=fake_response):
        result = AIContentService(session).generate_reflection(activity)

    assert result["learned"] == "느낀 점"
    assert result["next_action"] == "다음 행동"


def test_generate_reflection_parses_markdown_code_block(session):
    """AI가 ```json ... ``` 형태로 감싸서 답해도 정상 파싱되어야 한다."""
    activity = _make_activity(session)
    fake_response = "```json\n" + json.dumps({"learned": "A", "next_action": "B"}) + "\n```"

    with patch("ai.ai_client.AIClient.complete", return_value=fake_response):
        result = AIContentService(session).generate_reflection(activity)

    assert result["learned"] == "A"


def test_generate_reflection_raises_on_invalid_json(session):
    activity = _make_activity(session)
    with patch("ai.ai_client.AIClient.complete", return_value="이건 JSON이 아님"):
        with pytest.raises(ValueError):
            AIContentService(session).generate_reflection(activity)


def test_generate_reflection_raises_on_missing_keys(session):
    """JSON은 맞지만 필요한 키가 빠져있으면 에러가 나야 한다."""
    activity = _make_activity(session)
    fake_response = json.dumps({"learned": "느낀 점만 있음"})
    with patch("ai.ai_client.AIClient.complete", return_value=fake_response):
        with pytest.raises(ValueError):
            AIContentService(session).generate_reflection(activity)


def test_generate_and_save_interview_qa_persists_to_db(session):
    activity = _make_activity(session)
    fake_response = json.dumps({
        "items": [
            {"question": "Q1", "follow_up": "F1", "model_answer": "A1"},
            {"question": "Q2", "follow_up": "F2", "model_answer": "A2"},
            {"question": "Q3", "follow_up": "F3", "model_answer": "A3"},
        ]
    }, ensure_ascii=False)

    with patch("ai.ai_client.AIClient.complete", return_value=fake_response):
        saved = AIContentService(session).generate_and_save_interview_qa(activity)

    assert len(saved) == 3
    assert all(qa.id is not None for qa in saved)
    assert all(qa.is_ai_generated is True for qa in saved)

    from repositories.interview_qa_repository import InterviewQARepository
    reloaded = InterviewQARepository(session).list_by_activity(activity.id)
    assert len(reloaded) == 3
