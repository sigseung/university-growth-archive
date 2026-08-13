"""
services/ai_analysis_service.py

전체 활동 데이터를 통계로 요약해서 AI에게 "성장 분석 리포트"를 요청하고,
결과를 AIAnalysisLog에 저장합니다. (매번 새로 생성하지 않고 이력을 남겨서
'예전에 이런 분석을 받았었지' 하고 비교해볼 수 있게 하기 위함)
"""

import json

from sqlalchemy.orm import Session

from ai.ai_client import AIClient
from ai.prompts.growth_analysis_prompt import build_growth_analysis_prompt
from analytics.stats_calculator import build_summary_text
from models.ai_analysis_log import AIAnalysisLog
from repositories.ai_analysis_log_repository import AIAnalysisLogRepository
from services.activity_service import ActivityService


class AIAnalysisService:
    def __init__(self, session: Session):
        self.session = session
        self.repo = AIAnalysisLogRepository(session)
        self.activity_service = ActivityService(session)

    def generate_growth_analysis(self) -> AIAnalysisLog:
        activities = self.activity_service.list_activities()
        if not activities:
            raise ValueError("분석할 활동 기록이 아직 없습니다. 활동을 먼저 추가해주세요.")

        summary_text = build_summary_text(activities)
        system_prompt, user_prompt = build_growth_analysis_prompt(summary_text)

        content = AIClient().complete(system_prompt, user_prompt, max_tokens=700)

        related_ids_json = json.dumps([a.id for a in activities])
        return self.repo.create("성장분석", content, related_ids_json)

    def get_recent_logs(self, limit: int = 5) -> list[AIAnalysisLog]:
        return self.repo.get_recent(limit)

    def get_latest_log(self) -> AIAnalysisLog | None:
        logs = self.repo.get_recent(1)
        return logs[0] if logs else None
