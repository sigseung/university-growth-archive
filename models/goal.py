"""
models/goal.py

Goal(목표)은 "이번 학기에 공모전 3개 참가하기" 같은 목표를 기록하고,
연결된 활동들이 얼마나 채워졌는지로 진행률을 계산합니다.

진행률 계산 방식 (services/goal_service.py에서 실제 계산):
    - target_count(목표 활동 수)가 설정되어 있으면:
      진행률 = 연결된 완료(DONE) 활동 수 / target_count * 100 (자동 계산)
    - target_count가 없으면:
      progress_percent 컬럼값을 사용자가 직접 입력한 값 그대로 사용 (수동)
"""

import enum
from datetime import date, datetime

from sqlalchemy import String, Text, Integer, Boolean, DateTime, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base


class PeriodType(str, enum.Enum):
    YEARLY = "연간"
    SEMESTER = "학기"
    MONTHLY = "월간"
    WEEKLY = "주간"


class Goal(Base):
    __tablename__ = "goals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    period_type: Mapped[PeriodType] = mapped_column(Enum(PeriodType), default=PeriodType.SEMESTER)
    period_label: Mapped[str] = mapped_column(String(50))  # 예: "2026년", "2026-1학기"
    target_description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # target_count가 있으면 진행률이 연결된 활동 수 기준으로 자동 계산됩니다.
    target_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    progress_percent: Mapped[int] = mapped_column(Integer, default=0)  # 수동 입력 시 사용
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)

    # 이 목표를 위해 만들어진 활동들 (Activity.goal_id 로 연결)
    activities: Mapped[list["Activity"]] = relationship(back_populates="goal")

    def __repr__(self) -> str:
        return f"<Goal id={self.id} title={self.title!r}>"
