"""
tests/test_goal_service.py

목표(Goal) 진행률 자동 계산 로직이 정확한지 검증합니다.
이 프로젝트에서 "숫자가 틀리면 안 되는" 대표적인 로직이라 꼼꼼히 테스트합니다.
"""

from datetime import date

from models.activity import ActivityType, ActivityStatus
from models.goal import PeriodType
from services.activity_service import ActivityService
from services.goal_service import GoalService


def test_progress_auto_calculated_from_linked_activities(session):
    goal_service = GoalService(session)
    activity_service = ActivityService(session)

    goal = goal_service.create_goal(
        title="공모전 4개 참가하기", period_type=PeriodType.SEMESTER,
        period_label="2026-2학기", target_count=4,
    )

    # 완료 2개 + 진행중 1개(진행률 계산에 포함 안 됨) 연결
    a1 = activity_service.create_activity(
        title="공모전1", activity_type=ActivityType.CONTEST,
        date_start=date(2026, 3, 1), status=ActivityStatus.DONE,
    )
    a1.goal_id = goal.id
    a2 = activity_service.create_activity(
        title="공모전2", activity_type=ActivityType.CONTEST,
        date_start=date(2026, 4, 1), status=ActivityStatus.DONE,
    )
    a2.goal_id = goal.id
    a3 = activity_service.create_activity(
        title="공모전3(진행중)", activity_type=ActivityType.CONTEST,
        date_start=date(2026, 5, 1), status=ActivityStatus.ONGOING,
    )
    a3.goal_id = goal.id
    session.commit()
    session.refresh(goal)

    percent = goal_service.calculate_progress(goal)
    # 완료 2개 / 목표 4개 = 50%. 진행중인 활동은 분자에 포함되지 않아야 한다.
    assert percent == 50


def test_progress_uses_manual_value_when_no_target_count(session):
    goal_service = GoalService(session)
    goal = goal_service.create_goal(
        title="Python 프로젝트 완성", period_type=PeriodType.MONTHLY,
        period_label="2026년 9월", progress_percent=40,
    )
    assert goal_service.calculate_progress(goal) == 40


def test_progress_caps_at_100_percent(session):
    """목표보다 완료 활동이 더 많아도 100%를 넘지 않아야 한다."""
    goal_service = GoalService(session)
    activity_service = ActivityService(session)

    goal = goal_service.create_goal(
        title="세미나 1개 참가", period_type=PeriodType.MONTHLY,
        period_label="2026년 3월", target_count=1,
    )
    for i in range(3):
        a = activity_service.create_activity(
            title=f"세미나{i}", activity_type=ActivityType.SEMINAR,
            date_start=date(2026, 3, i + 1), status=ActivityStatus.DONE,
        )
        a.goal_id = goal.id
    session.commit()
    session.refresh(goal)

    assert goal_service.calculate_progress(goal) == 100


def test_progress_zero_when_no_linked_activities(session):
    goal_service = GoalService(session)
    goal = goal_service.create_goal(
        title="새 목표", period_type=PeriodType.WEEKLY,
        period_label="1주차", target_count=5,
    )
    assert goal_service.calculate_progress(goal) == 0
