"""
models/interview_qa.py

InterviewQA(면접 준비)는 활동 하나를 근거로 AI가 생성한
예상 질문 / 꼬리 질문 / 모범 답변을 저장합니다.
사용자가 직접 자신의 답변(user_answer)을 써보고 비교할 수도 있습니다.
"""

from datetime import datetime

from sqlalchemy import Text, DateTime, Integer, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base


class InterviewQA(Base):
    __tablename__ = "interview_qas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    activity_id: Mapped[int] = mapped_column(ForeignKey("activities.id"), nullable=False)

    question: Mapped[str] = mapped_column(Text, nullable=False)
    follow_up_question: Mapped[str | None] = mapped_column(Text, nullable=True)
    model_answer: Mapped[str | None] = mapped_column(Text, nullable=True)
    user_answer: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_ai_generated: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    activity: Mapped["Activity"] = relationship(back_populates="interview_qas")

    def __repr__(self) -> str:
        return f"<InterviewQA id={self.id} activity_id={self.activity_id}>"
