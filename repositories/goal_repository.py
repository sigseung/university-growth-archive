"""
repositories/goal_repository.py

Goal 테이블에 대한 순수 CRUD만 담당합니다. (규칙은 activity_repository.py와 동일)
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from models.goal import Goal


class GoalRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, goal: Goal) -> Goal:
        self.session.add(goal)
        self.session.commit()
        self.session.refresh(goal)
        return goal

    def get_by_id(self, goal_id: int) -> Goal | None:
        return self.session.get(Goal, goal_id)

    def get_all(self) -> list[Goal]:
        stmt = select(Goal).order_by(Goal.created_at.desc())
        return list(self.session.scalars(stmt).all())

    def update(self, goal: Goal) -> Goal:
        self.session.commit()
        self.session.refresh(goal)
        return goal

    def delete(self, goal_id: int) -> bool:
        goal = self.get_by_id(goal_id)
        if goal is None:
            return False
        self.session.delete(goal)
        self.session.commit()
        return True
