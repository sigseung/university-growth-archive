"""
utils/file_utils.py

첨부파일 기능에서 쓰는 파일 시스템 관련 헬퍼입니다.
'사용자가 고른 파일을 앱 전용 폴더로 복사'하고 '그 파일을 기본 프로그램으로 열기'
두 가지가 핵심입니다.
"""

import shutil
import subprocess
import sys
import uuid
from pathlib import Path

from config import ATTACHMENTS_DIR


def copy_file_to_storage(source_path: str, activity_id: int) -> str:
    """사용자가 선택한 파일을 앱의 첨부파일 저장소로 복사하고,
    저장된 경로(문자열)를 반환합니다.

    활동별로 폴더를 나누는 이유(assets/attachments/<activity_id>/):
    같은 이름의 파일(예: '참가증.pdf')을 여러 활동에서 올려도 충돌하지 않게 하기 위함입니다.
    파일명 앞에 uuid 일부를 붙이는 이유는 같은 활동 안에서도 동일 파일명 충돌을 막기 위함입니다.
    """
    source = Path(source_path)
    if not source.exists():
        raise FileNotFoundError(f"파일을 찾을 수 없습니다: {source_path}")

    activity_dir = ATTACHMENTS_DIR / str(activity_id)
    activity_dir.mkdir(parents=True, exist_ok=True)

    unique_prefix = uuid.uuid4().hex[:8]
    dest_name = f"{unique_prefix}_{source.name}"
    dest_path = activity_dir / dest_name

    shutil.copy2(source, dest_path)
    return str(dest_path)


def open_file_with_default_app(file_path: str) -> None:
    """OS 기본 프로그램으로 파일을 엽니다. (사진 뷰어, PDF 리더 등)"""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"파일을 찾을 수 없습니다: {file_path}")

    if sys.platform == "win32":
        import os
        os.startfile(path)  # type: ignore[attr-defined]
    elif sys.platform == "darwin":
        subprocess.run(["open", str(path)])
    else:
        subprocess.run(["xdg-open", str(path)])


def guess_attachment_type(file_path: str) -> str:
    """확장자를 보고 AttachmentType 값을 추측합니다. 업로드 시 기본값 설정용."""
    ext = Path(file_path).suffix.lower()
    mapping = {
        ".jpg": "사진", ".jpeg": "사진", ".png": "사진", ".gif": "사진", ".webp": "사진",
        ".mp4": "영상", ".mov": "영상", ".avi": "영상",
        ".pdf": "PDF",
        ".ppt": "PPT", ".pptx": "PPT",
        ".doc": "Word", ".docx": "Word",
        ".xls": "Excel", ".xlsx": "Excel",
    }
    return mapping.get(ext, "기타")
