"""
services/goal_service.py

목표 생성/조회와 함께, 이 서비스의 핵심 로직인
'진행률 자동 계산'을 담당합니다.

계산 규칙:
    target_count가 설정되어 있으면
        진행률 = (이 목표에 연결된 완료 상태 활동 수 / target_count) * 100  (최대 100)
    target_count가 없으면
        DB에 저장된 progress_percent를 그대로 사용 (사용자가 수동으로 입력)
"""

from sqlalchemy.orm import Session

from models.goal import Goal, PeriodType
from models.activity import ActivityStatus
from repositories.goal_repository import GoalRepository


class GoalService:
    def __init__(self, session: Session):
        self.session = session
        self.repo = GoalRepository(session)

    def create_goal(
        self,
        title: str,
        period_type: PeriodType,
        period_label: str,
        target_description: str | None = None,
        target_count: int | None = None,
        progress_percent: int = 0,
    ) -> Goal:
        if not title or not title.strip():
            raise ValueError("목표 제목은 비어있을 수 없습니다.")

        goal = Goal(
            title=title.strip(),
            period_type=period_type,
            period_label=period_label.strip(),
            target_description=target_description,
            target_count=target_count,
            progress_percent=progress_percent,
        )
        return self.repo.create(goal)

    def update_goal(self, goal_id: int, **fields) -> Goal:
        goal = self.repo.get_by_id(goal_id)
        if goal is None:
            raise ValueError(f"id={goal_id} 목표를 찾을 수 없습니다.")
        for key, value in fields.items():
            if hasattr(goal, key):
                setattr(goal, key, value)
        return self.repo.update(goal)

    def delete_goal(self, goal_id: int) -> bool:
        # 목표를 지우기 전에, 연결되어 있던 활동들의 goal_id를 먼저 해제합니다.
        # (SQLite는 기본적으로 외래키 제약을 강제하지 않아 그냥 지워도 에러는 안 나지만,
        #  goal_id가 존재하지 않는 목표를 가리키는 '유령 참조'로 남는 것을 막기 위함입니다.)
        goal = self.repo.get_by_id(goal_id)
        if goal is None:
            return False
        for activity in list(goal.activities):
            activity.goal_id = None
        self.session.commit()
        return self.repo.delete(goal_id)

    def get_goal(self, goal_id: int) -> Goal | None:
        return self.repo.get_by_id(goal_id)

    def list_goals(self) -> list[Goal]:
        return self.repo.get_all()

    def calculate_progress(self, goal: Goal) -> int:
        """목표의 실제 진행률(%)을 계산해서 돌려줍니다.
        (DB의 progress_percent 컬럼을 항상 신뢰하지 않고,
         target_count가 있으면 매번 실제 연결된 활동 수를 세어 다시 계산합니다.
         → '활동을 나중에 삭제해도 진행률이 자동으로 맞춰진다'는 장점이 있습니다.)"""
        if goal.target_count and goal.target_count > 0:
            done_count = sum(
                1 for a in goal.activities if a.status == ActivityStatus.DONE
            )
            percent = int((done_count / goal.target_count) * 100)
            return min(percent, 100)
        return goal.progress_percent

    def get_linked_activity_count(self, goal: Goal) -> tuple[int, int]:
        """(완료된 활동 수, 전체 연결된 활동 수) 튜플. 목표 카드에 'N/M' 형태로 표시하기 위함."""
        done = sum(1 for a in goal.activities if a.status == ActivityStatus.DONE)
        total = len(goal.activities)
        return done, total
