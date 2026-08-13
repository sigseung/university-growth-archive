"""
models/category.py

Category(자기소개서 분류)는 "협업", "리더십", "도전" 처럼
활동을 자기소개서 문항 관점에서 분류하는 태그입니다.

Tag(자유 검색 키워드)와 굳이 분리한 이유:
    - Tag는 사용자가 자유롭게 만드는 검색용 키워드입니다. (예: "AI", "삼성")
    - Category는 자기소개서/면접 준비라는 특정 목적을 위한 '고정된 관점'입니다.
      그래서 기본 9종을 미리 심어두고(seed), 화면에서도 버튼 형태로 고정 노출합니다.
    (같은 다대다 관계라도 '용도'가 다르면 테이블을 분리하는 편이
     나중에 "카테고리만 통계 내기" 같은 기능을 넣기 쉽습니다.)
"""

from sqlalchemy import String, Integer, Table, Column, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base

# 기본으로 심어둘 9종 카테고리. 설계 문서의 "자기소개서 관리" 섹션 기준.
DEFAULT_CATEGORY_NAMES = [
    "협업", "문제해결", "도전", "창의성", "리더십", "책임감", "성장", "실패경험", "성과",
]

activity_categories = Table(
    "activity_categories",
    Base.metadata,
    Column("activity_id", ForeignKey("activities.id"), primary_key=True),
    Column("category_id", ForeignKey("categories.id"), primary_key=True),
)


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    activities: Mapped[list["Activity"]] = relationship(
        secondary=activity_categories, back_populates="categories"
    )

    def __repr__(self) -> str:
        return f"<Category id={self.id} name={self.name!r}>"
