"""
repositories/attachment_repository.py

Attachment 테이블에 대한 순수 CRUD.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from models.attachment import Attachment


class AttachmentRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, attachment: Attachment) -> Attachment:
        self.session.add(attachment)
        self.session.commit()
        self.session.refresh(attachment)
        return attachment

    def get_by_id(self, attachment_id: int) -> Attachment | None:
        return self.session.get(Attachment, attachment_id)

    def get_by_activity(self, activity_id: int) -> list[Attachment]:
        stmt = select(Attachment).where(Attachment.activity_id == activity_id)
        return list(self.session.scalars(stmt).all())

    def delete(self, attachment_id: int) -> bool:
        attachment = self.get_by_id(attachment_id)
        if attachment is None:
            return False
        self.session.delete(attachment)
        self.session.commit()
        return True
