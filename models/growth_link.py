"""
models/growth_link.py

GrowthLink(성장 연결)는 이 프로젝트의 정체성이라 할 수 있는 테이블입니다.

"AI Summit 참가" → "Python 공부 시작" 처럼, 활동 A가 활동 B로 이어졌다는
인과관계를 저장합니다. Activity를 자기 자신과 연결하는 자기참조(self-referencing)
다대다 관계이고, 단순 연결이 아니라 "왜 연결되는지(link_reason)"까지 남길 수 있어서
Tag/Category처럼 단순 association table이 아니라 독립된 모델로 만들었습니다.

방향성이 있다는 점이 중요합니다: from_activity → to_activity.
(A가 B의 원인이다. B가 A의 원인이라는 뜻이 아님)
"""

from datetime import datetime

from sqlalchemy import Text, DateTime, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base


class GrowthLink(Base):
    __tablename__ = "growth_links"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    from_activity_id: Mapped[int] = mapped_column(ForeignKey("activities.id"), nullable=False)
    to_activity_id: Mapped[int] = mapped_column(ForeignKey("activities.id"), nullable=False)
    link_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    # 자기참조 관계라서 SQLAlchemy에게 "어느 FK를 기준으로 관계를 맺을지"를
    # foreign_keys로 명시해야 합니다 (안 그러면 from/to 둘 다 같은 컬럼으로 착각함).
    from_activity: Mapped["Activity"] = relationship(
        foreign_keys=[from_activity_id], back_populates="outgoing_links"
    )
    to_activity: Mapped["Activity"] = relationship(
        foreign_keys=[to_activity_id], back_populates="incoming_links"
    )

    def __repr__(self) -> str:
        return f"<GrowthLink {self.from_activity_id} -> {self.to_activity_id}>"
