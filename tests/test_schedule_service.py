"""
tests/test_schedule_service.py

일정 생성과 "월별 조회 + 날짜별 그룹핑"이 달력 화면이 기대하는 형태로
정확히 동작하는지 검증합니다.
"""

from datetime import date

from models.schedule import ScheduleType
from services.schedule_service import ScheduleService


def test_create_schedule(session):
    service = ScheduleService(session)
    schedule = service.create_schedule(
        title="SQLD 시험", schedule_date=date(2026, 9, 20), schedule_type=ScheduleType.EXAM,
    )
    assert schedule.id is not None
    assert schedule.title == "SQLD 시험"


def test_get_month_schedules_filters_by_month(session):
    service = ScheduleService(session)
    service.create_schedule(title="9월 일정", schedule_date=date(2026, 9, 5), schedule_type=ScheduleType.EXAM)
    service.create_schedule(title="10월 일정", schedule_date=date(2026, 10, 5), schedule_type=ScheduleType.FAIR)

    september = service.get_month_schedules(2026, 9)
    assert len(september) == 1
    assert september[0].title == "9월 일정"


def test_group_by_day(session):
    service = ScheduleService(session)
    service.create_schedule(title="A", schedule_date=date(2026, 9, 5), schedule_type=ScheduleType.EXAM)
    service.create_schedule(title="B", schedule_date=date(2026, 9, 5), schedule_type=ScheduleType.FAIR)
    service.create_schedule(title="C", schedule_date=date(2026, 9, 10), schedule_type=ScheduleType.ETC)

    schedules = service.get_month_schedules(2026, 9)
    grouped = service.group_by_day(schedules)

    assert len(grouped[5]) == 2  # 같은 날짜에 2개
    assert len(grouped[10]) == 1
