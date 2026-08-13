"""
repositories/schedule_repository.py

Schedule 테이블에 대한 순수 CRUD만 담당합니다.
"""

from datetime import date

from sqlalchemy import select, extract
from sqlalchemy.orm import Session

from models.schedule import Schedule


class ScheduleRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, schedule: Schedule) -> Schedule:
        self.session.add(schedule)
        self.session.commit()
        self.session.refresh(schedule)
        return schedule

    def get_by_id(self, schedule_id: int) -> Schedule | None:
        return self.session.get(Schedule, schedule_id)

    def get_all(self) -> list[Schedule]:
        stmt = select(Schedule).order_by(Schedule.date.asc())
        return list(self.session.scalars(stmt).all())

    def get_by_month(self, year: int, month: int) -> list[Schedule]:
        """달력 뷰에서 특정 연-월의 일정만 가져올 때 사용."""
        stmt = (
            select(Schedule)
            .where(extract("year", Schedule.date) == year)
            .where(extract("month", Schedule.date) == month)
            .order_by(Schedule.date.asc())
        )
        return list(self.session.scalars(stmt).all())

    def get_upcoming(self, today: date | None = None, limit: int = 10) -> list[Schedule]:
        today = today or date.today()
        stmt = (
            select(Schedule)
            .where(Schedule.date >= today)
            .order_by(Schedule.date.asc())
            .limit(limit)
        )
        return list(self.session.scalars(stmt).all())

    def delete(self, schedule_id: int) -> bool:
        schedule = self.get_by_id(schedule_id)
        if schedule is None:
            return False
        self.session.delete(schedule)
        self.session.commit()
        return True
