"""
tests/test_growth_link_service.py

GrowthLink(성장 연결)의 핵심 규칙 — 자기 자신 연결 금지, 연결/해제,
방향성(outgoing/incoming)이 올바른지 검증합니다.
"""

from datetime import date

import pytest

from models.activity import ActivityType
from services.activity_service import ActivityService
from services.growth_link_service import GrowthLinkService


def _make_activity(activity_service, title, day):
    return activity_service.create_activity(
        title=title, activity_type=ActivityType.PROJECT, date_start=date(2026, 1, day),
    )


def test_link_activities_creates_directed_link(session):
    activity_service = ActivityService(session)
    link_service = GrowthLinkService(session)

    a1 = _make_activity(activity_service, "활동1", 1)
    a2 = _make_activity(activity_service, "활동2", 2)

    link = link_service.link_activities(a1.id, a2.id, reason="자연스러운 다음 단계")
    assert link.from_activity_id == a1.id
    assert link.to_activity_id == a2.id
    assert link.link_reason == "자연스러운 다음 단계"

    session.refresh(a1)
    session.refresh(a2)
    assert len(a1.outgoing_links) == 1
    assert len(a1.incoming_links) == 0
    assert len(a2.incoming_links) == 1
    assert len(a2.outgoing_links) == 0


def test_link_activities_rejects_self_link(session):
    activity_service = ActivityService(session)
    link_service = GrowthLinkService(session)

    a1 = _make_activity(activity_service, "활동1", 1)

    with pytest.raises(ValueError):
        link_service.link_activities(a1.id, a1.id)


def test_unlink_removes_the_link(session):
    activity_service = ActivityService(session)
    link_service = GrowthLinkService(session)

    a1 = _make_activity(activity_service, "활동1", 1)
    a2 = _make_activity(activity_service, "활동2", 2)
    link = link_service.link_activities(a1.id, a2.id)

    assert link_service.unlink(link.id) is True
    session.refresh(a1)
    assert len(a1.outgoing_links) == 0
    # 이미 삭제된 연결을 다시 지우려 하면 False
    assert link_service.unlink(link.id) is False


def test_deleting_activity_cascades_its_links(session):
    """활동을 삭제하면, 그 활동에 걸려있던 연결도 함께 삭제되어야 한다
    (models/activity.py의 cascade='all, delete-orphan' 설정 검증)."""
    activity_service = ActivityService(session)
    link_service = GrowthLinkService(session)

    a1 = _make_activity(activity_service, "활동1", 1)
    a2 = _make_activity(activity_service, "활동2", 2)
    link_service.link_activities(a1.id, a2.id)

    activity_service.delete_activity(a1.id)

    all_links = link_service.get_all_links()
    assert len(all_links) == 0
