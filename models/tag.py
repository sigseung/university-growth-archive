"""
models/tag.py

Tag(태그)는 "반도체", "AI", "Python", "GitHub" 처럼 자유롭게 붙이는
검색용 키워드입니다. 하나의 활동에 여러 태그가 붙고,
하나의 태그도 여러 활동에 붙을 수 있으므로 N:M(다대다) 관계입니다.

다대다 관계는 SQLAlchemy에서 '연결 테이블(association table)'을
따로 하나 둬야 합니다. 그게 바로 activity_tags 입니다.
"""

from sqlalchemy import String, Integer, Table, Column, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base

# 다대다 연결 테이블. 별도 클래스 없이 Table로만 정의해도 충분합니다
# (이 테이블 자체에 추가 데이터를 저장할 필요가 없기 때문).
activity_tags = Table(
    "activity_tags",
    Base.metadata,
    Column("activity_id", ForeignKey("activities.id"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id"), primary_key=True),
)


class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    activities: Mapped[list["Activity"]] = relationship(
        secondary=activity_tags, back_populates="tags"
    )

    def __repr__(self) -> str:
        return f"<Tag id={self.id} name={self.name!r}>"
