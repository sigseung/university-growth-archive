"""
models/attachment.py

Attachment(첨부파일)는 활동에 딸린 사진/PDF/PPT/참가증 등을 기록합니다.
실제 파일은 DB에 저장하지 않고, 파일 시스템에 복사해둔 뒤
그 '경로(file_path)'만 DB에 저장합니다. (DB에 바이너리를 직접 넣지 않는 이유:
DB 파일이 비대해지고 백업/이관이 느려지기 때문입니다.)
"""

import enum
from datetime import datetime

from sqlalchemy import String, DateTime, Integer, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base


class AttachmentType(str, enum.Enum):
    PHOTO = "사진"
    VIDEO = "영상"
    PDF = "PDF"
    PPT = "PPT"
    WORD = "Word"
    EXCEL = "Excel"
    BROCHURE = "브로슈어"
    CERTIFICATE = "참가증"
    ETC = "기타"


class Attachment(Base):
    __tablename__ = "attachments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    activity_id: Mapped[int] = mapped_column(ForeignKey("activities.id"), nullable=False)

    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_type: Mapped[AttachmentType] = mapped_column(
        Enum(AttachmentType), nullable=False, default=AttachmentType.ETC
    )
    original_name: Mapped[str | None] = mapped_column(String(255), nullable=True)

    uploaded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    activity: Mapped["Activity"] = relationship(back_populates="attachments")

    def __repr__(self) -> str:
        return f"<Attachment id={self.id} type={self.file_type}>"
