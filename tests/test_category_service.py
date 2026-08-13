"""
tests/test_category_service.py

기본 9종 카테고리 시드가 중복 생성 없이 정확히 동작하는지,
카테고리별 활동 집계가 맞는지 검증합니다.
"""

from datetime import date

from models.activity import ActivityType
from models.category import DEFAULT_CATEGORY_NAMES
from services.activity_service import ActivityService
from services.category_service import CategoryService


def test_ensure_default_categories_creates_nine(session):
    # conftest.py의 session fixture가 이미 시드를 한 번 호출하지만,
    # 멱등성(여러 번 호출해도 안전한지)을 확인하기 위해 한 번 더 호출합니다.
    service = CategoryService(session)
    service.ensure_default_categories()
    service.ensure_default_categories()

    categories = service.list_categories()
    assert len(categories) == len(DEFAULT_CATEGORY_NAMES)
    assert {c.name for c in categories} == set(DEFAULT_CATEGORY_NAMES)


def test_count_activities_by_category(session):
    activity_service = ActivityService(session)
    category_service = CategoryService(session)

    activity_service.create_activity(
        title="협업 활동1", activity_type=ActivityType.PROJECT,
        date_start=date(2026, 1, 1), category_names=["협업"],
    )
    activity_service.create_activity(
        title="협업 활동2", activity_type=ActivityType.CLUB,
        date_start=date(2026, 2, 1), category_names=["협업", "리더십"],
    )

    counts = category_service.count_activities_by_category()
    assert counts["협업"] == 2
    assert counts["리더십"] == 1
    assert counts["도전"] == 0
