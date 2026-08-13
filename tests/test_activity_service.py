"""
tests/test_activity_service.py

ActivityService의 핵심 동작(생성/수정/삭제/검색/태그/카테고리 배정)을 검증합니다.
`session` fixture는 conftest.py에서 정의되며, 테스트마다 완전히 새로운
임시 DB를 만들어주므로 테스트끼리 서로 데이터에 영향을 주지 않습니다.
"""

from datetime import date

import pytest

from models.activity import ActivityType, ActivityStatus
from services.activity_service import ActivityService


def _make_service(session):
    return ActivityService(session)


def test_create_activity_minimal(session):
    """제목/종류/시작일만으로도 활동을 만들 수 있어야 한다 (필수값 최소화)."""
    service = _make_service(session)
    activity = service.create_activity(
        title="AI 세미나", activity_type=ActivityType.SEMINAR, date_start=date(2026, 3, 1),
    )
    assert activity.id is not None
    assert activity.status == ActivityStatus.PLANNED  # 기본값
    assert activity.importance == 3  # 기본값


def test_create_activity_rejects_empty_title(session):
    service = _make_service(session)
    with pytest.raises(ValueError):
        service.create_activity(
            title="   ", activity_type=ActivityType.SEMINAR, date_start=date(2026, 3, 1),
        )


def test_create_activity_rejects_invalid_importance(session):
    service = _make_service(session)
    with pytest.raises(ValueError):
        service.create_activity(
            title="세미나", activity_type=ActivityType.SEMINAR,
            date_start=date(2026, 3, 1), importance=10,
        )


def test_create_activity_with_tags_reuses_existing_tag(session):
    """같은 이름의 태그를 두 번 쓰면, 태그 레코드가 중복 생성되지 않고 재사용되어야 한다."""
    service = _make_service(session)
    a1 = service.create_activity(
        title="활동1", activity_type=ActivityType.SEMINAR,
        date_start=date(2026, 1, 1), tag_names=["AI", "반도체"],
    )
    a2 = service.create_activity(
        title="활동2", activity_type=ActivityType.PROJECT,
        date_start=date(2026, 2, 1), tag_names=["AI"],
    )
    assert {t.name for t in a1.tags} == {"AI", "반도체"}
    # 같은 이름의 태그 객체(id)를 공유해야 한다 (재생성 아님)
    ai_tag_from_a1 = next(t for t in a1.tags if t.name == "AI")
    ai_tag_from_a2 = next(t for t in a2.tags if t.name == "AI")
    assert ai_tag_from_a1.id == ai_tag_from_a2.id


def test_update_activity_changes_fields(session):
    service = _make_service(session)
    activity = service.create_activity(
        title="원래 제목", activity_type=ActivityType.SEMINAR, date_start=date(2026, 1, 1),
    )
    updated = service.update_activity(activity.id, title="바뀐 제목", importance=5)
    assert updated.title == "바뀐 제목"
    assert updated.importance == 5


def test_update_activity_missing_id_raises(session):
    service = _make_service(session)
    with pytest.raises(ValueError):
        service.update_activity(999, title="없는 활동")


def test_delete_activity(session):
    service = _make_service(session)
    activity = service.create_activity(
        title="삭제할 활동", activity_type=ActivityType.SEMINAR, date_start=date(2026, 1, 1),
    )
    assert service.delete_activity(activity.id) is True
    assert service.get_activity(activity.id) is None
    assert service.delete_activity(activity.id) is False  # 이미 삭제됨


def test_search_activities_matches_title_and_content(session):
    service = _make_service(session)
    service.create_activity(
        title="AI Summit 참가", activity_type=ActivityType.SEMINAR,
        date_start=date(2026, 1, 1), content="반도체 산업 관련 발표",
    )
    service.create_activity(
        title="교내 봉사활동", activity_type=ActivityType.VOLUNTEER, date_start=date(2026, 2, 1),
    )

    by_title = service.search_activities("AI")
    assert len(by_title) == 1

    by_content = service.search_activities("반도체")
    assert len(by_content) == 1

    no_match = service.search_activities("존재하지않는키워드")
    assert len(no_match) == 0


def test_get_activities_by_category(session):
    service = _make_service(session)
    a1 = service.create_activity(
        title="협업 활동", activity_type=ActivityType.PROJECT,
        date_start=date(2026, 1, 1), category_names=["협업"],
    )
    service.create_activity(
        title="개인 활동", activity_type=ActivityType.READING, date_start=date(2026, 2, 1),
    )

    collab_category = a1.categories[0]
    results = service.get_activities_by_category(collab_category.id)
    assert len(results) == 1
    assert results[0].id == a1.id


def test_dashboard_stats(session):
    service = _make_service(session)
    service.create_activity(
        title="완료된 활동", activity_type=ActivityType.SEMINAR,
        date_start=date(2026, 1, 1), status=ActivityStatus.DONE,
    )
    service.create_activity(
        title="예정된 활동", activity_type=ActivityType.CONTEST,
        date_start=date(2026, 5, 1), status=ActivityStatus.PLANNED,
    )

    stats = service.get_dashboard_stats()
    assert stats["total"] == 2
    assert stats["done"] == 1
    assert stats["upcoming"] == 1
