"""
models/schedule.py

Schedule(일정)은 달력에 표시되는 항목입니다.
Activity와는 별개 테이블인 이유: 아직 Activity로 기록하지 않은
'예정된 시험/접수 마감' 같은 것도 미리 달력에 적어두고 싶을 수 있기 때문입니다.
(activity_id가 있으면 해당 활동 상세로 바로 이동할 수 있게 연결만 해둡니다.)
"""

import enum
from datetime import date, datetime

from sqlalchemy import String, Date, DateTime, Integer, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base


class ScheduleType(str, enum.Enum):
    FAIR = "박람회"
    SEMINAR = "세미나"
    EXAM = "시험"
    CONTEST = "공모전"
    CERTIFICATE = "자격증"
    ETC = "기타"


class Schedule(Base):
    __tablename__ = "schedules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    schedule_type: Mapped[ScheduleType] = mapped_column(Enum(ScheduleType), default=ScheduleType.ETC)

    activity_id: Mapped[int | None] = mapped_column(ForeignKey("activities.id"), nullable=True)
    memo: Mapped[str | None] = mapped_column(String(300), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    activity: Mapped["Activity | None"] = relationship()

    def __repr__(self) -> str:
        return f"<Schedule id={self.id} title={self.title!r} date={self.date}>"
