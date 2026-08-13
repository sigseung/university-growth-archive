"""
models/ai_analysis_log.py

AI가 생성한 "성장 분석" 리포트를 매번 새로 만들지 않고 이력으로 저장해둡니다.
대시보드의 '최근 AI 분석' 카드와, AI 분석 화면의 '과거 분석 이력'에서 사용합니다.

related_activity_ids는 "이 분석이 어떤 활동들을 근거로 만들어졌는지"를
JSON 문자열(예: "[1, 5, 12]")로 저장합니다. 굳이 별도 N:M 테이블을 만들지 않은 이유:
이 정보는 '참고용 기록'일 뿐 활동 쪽에서 역참조할 일이 없어서, 관계형으로
모델링하는 것보다 JSON 텍스트로 두는 게 훨씬 간단하고 충분합니다.
"""

from datetime import datetime

from sqlalchemy import String, Text, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class AIAnalysisLog(Base):
    __tablename__ = "ai_analysis_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    analysis_type: Mapped[str] = mapped_column(String(50), nullable=False)  # 예: "성장분석"
    content: Mapped[str] = mapped_column(Text, nullable=False)
    related_activity_ids: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON 문자열
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    def __repr__(self) -> str:
        return f"<AIAnalysisLog id={self.id} type={self.analysis_type!r}>"
