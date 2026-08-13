"""
models/reflection.py

Reflection(회고)은 하나의 Activity에 여러 개 달릴 수 있습니다.
예: 활동 직후 남기는 회고 + 한 달 뒤 다시 돌아보며 남기는 회고.
그래서 Activity : Reflection = 1 : N 관계로 설계했습니다.
"""

from datetime import datetime

from sqlalchemy import Text, DateTime, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base


class Reflection(Base):
    __tablename__ = "reflections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    activity_id: Mapped[int] = mapped_column(ForeignKey("activities.id"), nullable=False)

    learned: Mapped[str | None] = mapped_column(Text, nullable=True)       # 느낀 점
    next_action: Mapped[str | None] = mapped_column(Text, nullable=True)   # 앞으로 할 행동

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    activity: Mapped["Activity"] = relationship(back_populates="reflections")

    def __repr__(self) -> str:
        return f"<Reflection id={self.id} activity_id={self.activity_id}>"
