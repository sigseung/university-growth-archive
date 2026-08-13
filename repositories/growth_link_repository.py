"""
repositories/growth_link_repository.py

GrowthLink 테이블에 대한 순수 CRUD.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from models.growth_link import GrowthLink


class GrowthLinkRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, from_activity_id: int, to_activity_id: int, link_reason: str | None) -> GrowthLink:
        link = GrowthLink(
            from_activity_id=from_activity_id,
            to_activity_id=to_activity_id,
            link_reason=link_reason,
        )
        self.session.add(link)
        self.session.commit()
        self.session.refresh(link)
        return link

    def get_all(self) -> list[GrowthLink]:
        """커리어 타임라인 화면에서 '전체 연결선'을 한 번에 그리기 위해 사용."""
        stmt = select(GrowthLink)
        return list(self.session.scalars(stmt).all())

    def delete(self, link_id: int) -> bool:
        link = self.session.get(GrowthLink, link_id)
        if link is None:
            return False
        self.session.delete(link)
        self.session.commit()
        return True
