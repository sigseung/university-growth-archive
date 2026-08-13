"""
repositories/interview_qa_repository.py

InterviewQA 테이블에 대한 순수 CRUD.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from models.interview_qa import InterviewQA


class InterviewQARepository:
    def __init__(self, session: Session):
        self.session = session

    def create(
        self, activity_id: int, question: str, follow_up_question: str | None = None,
        model_answer: str | None = None, is_ai_generated: bool = True,
    ) -> InterviewQA:
        qa = InterviewQA(
            activity_id=activity_id, question=question,
            follow_up_question=follow_up_question, model_answer=model_answer,
            is_ai_generated=is_ai_generated,
        )
        self.session.add(qa)
        self.session.commit()
        self.session.refresh(qa)
        return qa

    def list_by_activity(self, activity_id: int) -> list[InterviewQA]:
        stmt = (
            select(InterviewQA)
            .where(InterviewQA.activity_id == activity_id)
            .order_by(InterviewQA.created_at.asc())
        )
        return list(self.session.scalars(stmt).all())

    def update_user_answer(self, qa_id: int, user_answer: str) -> InterviewQA | None:
        qa = self.session.get(InterviewQA, qa_id)
        if qa is None:
            return None
        qa.user_answer = user_answer
        self.session.commit()
        self.session.refresh(qa)
        return qa

    def delete(self, qa_id: int) -> bool:
        qa = self.session.get(InterviewQA, qa_id)
        if qa is None:
            return False
        self.session.delete(qa)
        self.session.commit()
        return True
