"""
services/category_service.py

카테고리 목록 조회 + "기본 9종이 없으면 심어둔다(seed)"를 담당합니다.
활동에 카테고리를 실제로 배정하는 로직은 activity_service.py 쪽에
(_resolve_categories) 있습니다. (태그와 동일한 패턴 — Activity를
수정하는 주체는 항상 ActivityService 하나로 모아두기 위함입니다.)
"""

from sqlalchemy.orm import Session

from models.category import Category, DEFAULT_CATEGORY_NAMES
from repositories.category_repository import CategoryRepository


class CategoryService:
    def __init__(self, session: Session):
        self.session = session
        self.repo = CategoryRepository(session)

    def ensure_default_categories(self) -> None:
        """앱 시작 시 한 번 호출. 기본 9종 카테고리가 없으면 만들어둡니다."""
        for name in DEFAULT_CATEGORY_NAMES:
            self.repo.get_or_create(name)

    def list_categories(self) -> list[Category]:
        return self.repo.get_all()

    def get_category(self, category_id: int) -> Category | None:
        return self.repo.get_by_id(category_id)

    def count_activities_by_category(self) -> dict[str, int]:
        """카테고리 관리 화면에서 '카테고리별 활동 개수'를 보여주기 위한 집계."""
        return {c.name: len(c.activities) for c in self.list_categories()}
