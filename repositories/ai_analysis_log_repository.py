"""
repositories/ai_analysis_log_repository.py

AIAnalysisLog 테이블에 대한 순수 CRUD.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from models.ai_analysis_log import AIAnalysisLog


class AIAnalysisLogRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, analysis_type: str, content: str, related_activity_ids_json: str | None) -> AIAnalysisLog:
        log = AIAnalysisLog(
            analysis_type=analysis_type, content=content,
            related_activity_ids=related_activity_ids_json,
        )
        self.session.add(log)
        self.session.commit()
        self.session.refresh(log)
        return log

    def get_recent(self, limit: int = 5) -> list[AIAnalysisLog]:
        stmt = select(AIAnalysisLog).order_by(AIAnalysisLog.created_at.desc()).limit(limit)
        return list(self.session.scalars(stmt).all())
