"""
services/backup_service.py

SQLite DB 파일 하나를 통째로 복사하는 방식으로 백업/복원을 구현합니다.
(활동 수 년 규모의 개인 기록은 DB 파일 자체가 수 MB 수준이라,
행 단위로 백업 로직을 짜는 것보다 파일 복사가 훨씬 간단하고 안전합니다.)

전략:
    - 앱을 실행할 때마다 '오늘 날짜로 만든 백업이 아직 없으면' 자동으로 하나 만듭니다.
    - 최근 14개(약 2주치)만 남기고 오래된 백업은 자동으로 지웁니다.
    - 설정 화면에서 수동으로 즉시 백업하거나, 과거 백업으로 복원할 수 있습니다.
"""

import shutil
from datetime import datetime
from pathlib import Path

from config import DATABASE_PATH, BACKUPS_DIR, DATABASE_URL

MAX_BACKUPS = 14  # 최근 며칠치까지 보관할지 (자동 백업이 하루 1개이므로 약 2주치)
_BACKUP_PREFIX = "uga_backup_"


def create_backup() -> Path:
    """지금 시점의 DB 파일을 backups/ 폴더에 타임스탬프 이름으로 복사합니다."""
    if not DATABASE_PATH.exists():
        raise FileNotFoundError("아직 생성된 데이터베이스가 없습니다. 활동을 먼저 추가해보세요.")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = BACKUPS_DIR / f"{_BACKUP_PREFIX}{timestamp}.db"

    # shutil.copy2: 메타데이터(수정시각 등)까지 함께 복사. 단순 copy보다
    # '언제 백업했는지'를 파일 자체 속성으로도 남길 수 있어서 이걸 씁니다.
    shutil.copy2(DATABASE_PATH, backup_path)

    _prune_old_backups()
    return backup_path


def _prune_old_backups() -> None:
    """오래된 백업을 MAX_BACKUPS개만 남기고 삭제합니다."""
    backups = list_backups()
    for old in backups[MAX_BACKUPS:]:
        old.unlink(missing_ok=True)


def list_backups() -> list[Path]:
    """최신 순으로 정렬된 백업 파일 목록."""
    if not BACKUPS_DIR.exists():
        return []
    files = list(BACKUPS_DIR.glob(f"{_BACKUP_PREFIX}*.db"))
    return sorted(files, key=lambda p: p.stat().st_mtime, reverse=True)


def has_backup_today() -> bool:
    today_str = datetime.now().strftime("%Y%m%d")
    return any(p.name.startswith(f"{_BACKUP_PREFIX}{today_str}") for p in list_backups())


def auto_backup_if_needed() -> Path | None:
    """앱 시작 시 한 번 호출합니다. 오늘 이미 백업이 있으면 아무것도 안 하고,
    없으면 새로 하나 만듭니다. 실패하더라도(디스크 부족 등) 예외를 앱까지
    전파하지 않습니다 — 백업 실패가 앱 실행 자체를 막아서는 안 되기 때문입니다."""
    if not DATABASE_PATH.exists() or has_backup_today():
        return None
    try:
        return create_backup()
    except OSError:
        return None


def restore_backup(backup_path: Path) -> None:
    """선택한 백업 파일로 현재 DB를 되돌립니다.

    복원 직전에 현재 상태도 안전하게 하나 백업해둡니다 ('복원을 잘못 눌렀을 때'를
    위한 안전장치). 그 다음 DB 연결을 정리(dispose)하고 파일을 교체한 뒤,
    새 연결로 다시 설정합니다 — 이렇게 하면 앱을 재시작하지 않아도 복원 내용이
    바로 반영됩니다."""
    if not backup_path.exists():
        raise FileNotFoundError("선택한 백업 파일을 찾을 수 없습니다.")

    if DATABASE_PATH.exists():
        safety_name = f"{_BACKUP_PREFIX}before_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        shutil.copy2(DATABASE_PATH, BACKUPS_DIR / safety_name)

    # 순환 import를 피하기 위해 함수 안에서 import합니다.
    from database.db_session import configure

    shutil.copy2(backup_path, DATABASE_PATH)
    configure(DATABASE_URL)  # 새로 복원된 파일을 바라보는 연결로 재설정


def format_backup_label(backup_path: Path) -> str:
    """파일명(uga_backup_20260810_140500.db)을 사람이 읽기 좋은 라벨로 변환."""
    name = backup_path.stem.replace(_BACKUP_PREFIX, "")
    try:
        dt = datetime.strptime(name, "%Y%m%d_%H%M%S")
        label = dt.strftime("%Y-%m-%d %H:%M")
    except ValueError:
        label = name  # before_restore_ 같은 안전 백업은 원본 이름 그대로 표시

    size_kb = backup_path.stat().st_size / 1024
    return f"{label}  ({size_kb:.0f} KB)"
