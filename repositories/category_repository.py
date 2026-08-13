"""
repositories/category_repository.py

Category 테이블에 대한 순수 CRUD.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from models.category import Category


class CategoryRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_or_create(self, name: str) -> Category:
        """이름으로 카테고리를 찾고, 없으면 새로 만듭니다.
        (기본 9종 시드 + 사용자가 새 카테고리를 추가하는 경우 둘 다 이 메서드로 처리)"""
        existing = self.session.query(Category).filter_by(name=name).first()
        if existing:
            return existing
        category = Category(name=name)
        self.session.add(category)
        self.session.commit()
        self.session.refresh(category)
        return category

    def get_all(self) -> list[Category]:
        stmt = select(Category).order_by(Category.id.asc())
        return list(self.session.scalars(stmt).all())

    def get_by_id(self, category_id: int) -> Category | None:
        return self.session.get(Category, category_id)
