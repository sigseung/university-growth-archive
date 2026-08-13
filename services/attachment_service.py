"""
services/attachment_service.py

'파일을 저장소로 복사'하는 파일시스템 작업과 'DB에 기록'하는 작업을
하나의 흐름으로 묶어줍니다. 둘 중 하나만 실패해도 이상한 상태가 남지 않도록
파일 복사가 실패하면 DB에는 아예 기록하지 않습니다.
"""

from sqlalchemy.orm import Session

from models.attachment import Attachment, AttachmentType
from repositories.attachment_repository import AttachmentRepository
from utils.file_utils import copy_file_to_storage, guess_attachment_type


class AttachmentService:
    def __init__(self, session: Session):
        self.session = session
        self.repo = AttachmentRepository(session)

    def upload_attachment(self, activity_id: int, source_file_path: str) -> Attachment:
        # 1) 파일을 앱 전용 저장소로 복사 (여기서 예외가 나면 DB에 아무것도 남기지 않음)
        stored_path = copy_file_to_storage(source_file_path, activity_id)

        # 2) 확장자로 타입 추측
        type_value = guess_attachment_type(source_file_path)
        attachment_type = AttachmentType(type_value)

        from pathlib import Path
        original_name = Path(source_file_path).name

        attachment = Attachment(
            activity_id=activity_id,
            file_path=stored_path,
            file_type=attachment_type,
            original_name=original_name,
        )
        return self.repo.create(attachment)

    def list_attachments(self, activity_id: int) -> list[Attachment]:
        return self.repo.get_by_activity(activity_id)

    def delete_attachment(self, attachment_id: int) -> bool:
        # 참고: 실제 파일은 지우지 않고 DB 기록만 삭제합니다.
        # (실수로 지운 경우 파일 자체는 assets/attachments에 남아있어 복구 여지가 있습니다.
        #  완전 삭제가 필요하면 V6 '백업/정리' 기능에서 별도로 처리합니다.)
        return self.repo.delete(attachment_id)
