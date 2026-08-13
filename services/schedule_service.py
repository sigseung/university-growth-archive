"""
services/schedule_service.py

일정 생성/조회 로직. 달력 뷰가 '해당 월의 일정을 날짜별로 묶어서'
필요로 하기 때문에, 그 형태로 가공해주는 group_by_day()가 핵심입니다.
"""

from datetime import date
from collections import defaultdict

from sqlalchemy.orm import Session

from models.schedule import Schedule, ScheduleType
from repositories.schedule_repository import ScheduleRepository


class ScheduleService:
    def __init__(self, session: Session):
        self.session = session
        self.repo = ScheduleRepository(session)

    def create_schedule(
        self,
        title: str,
        schedule_date: date,
        schedule_type: ScheduleType = ScheduleType.ETC,
        activity_id: int | None = None,
        memo: str | None = None,
    ) -> Schedule:
        if not title or not title.strip():
            raise ValueError("일정 제목은 비어있을 수 없습니다.")

        schedule = Schedule(
            title=title.strip(),
            date=schedule_date,
            schedule_type=schedule_type,
            activity_id=activity_id,
            memo=memo,
        )
        return self.repo.create(schedule)

    def delete_schedule(self, schedule_id: int) -> bool:
        return self.repo.delete(schedule_id)

    def get_month_schedules(self, year: int, month: int) -> list[Schedule]:
        return self.repo.get_by_month(year, month)

    def get_upcoming(self, limit: int = 10) -> list[Schedule]:
        return self.repo.get_upcoming(limit=limit)

    def group_by_day(self, schedules: list[Schedule]) -> dict[int, list[Schedule]]:
        """일정 목록을 {일(day): [Schedule, ...]} 형태로 묶어줍니다.
        달력의 각 날짜 칸에 그날의 일정을 표시할 때 사용."""
        grouped: dict[int, list[Schedule]] = defaultdict(list)
        for s in schedules:
            grouped[s.date.day].append(s)
        return grouped
