"""
services/growth_link_service.py

활동 간 성장 연결(GrowthLink)을 만들고 조회하는 로직.
"""

from sqlalchemy.orm import Session

from models.growth_link import GrowthLink
from repositories.growth_link_repository import GrowthLinkRepository


class GrowthLinkService:
    def __init__(self, session: Session):
        self.session = session
        self.repo = GrowthLinkRepository(session)

    def link_activities(
        self, from_activity_id: int, to_activity_id: int, reason: str | None = None
    ) -> GrowthLink:
        if from_activity_id == to_activity_id:
            raise ValueError("같은 활동을 자기 자신에게 연결할 수는 없습니다.")
        return self.repo.create(from_activity_id, to_activity_id, reason)

    def unlink(self, link_id: int) -> bool:
        return self.repo.delete(link_id)

    def get_all_links(self) -> list[GrowthLink]:
        return self.repo.get_all()
