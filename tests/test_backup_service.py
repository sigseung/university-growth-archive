"""
tests/test_backup_service.py

백업 생성/복원 로직을 검증합니다. 실제 사용자 DB가 아니라
tmp_path로 만든 임시 파일들로 완전히 격리해서 테스트합니다.
"""

from datetime import date

from services import backup_service
from services.activity_service import ActivityService
from models.activity import ActivityType


def test_create_backup_copies_db_file(session, tmp_path, monkeypatch):
    import config

    fake_backups_dir = tmp_path / "backups"
    fake_backups_dir.mkdir()

    # session fixture가 이미 실제 임시 DB(tmp_path/test_uga.db)에 연결되어 있으므로,
    # config.DATABASE_PATH가 그 파일을 가리키도록 맞춰줍니다 (create_backup은 이 경로를 읽음).
    monkeypatch.setattr(config, "DATABASE_PATH", tmp_path / "test_uga.db")
    monkeypatch.setattr(backup_service, "DATABASE_PATH", tmp_path / "test_uga.db")
    monkeypatch.setattr(config, "BACKUPS_DIR", fake_backups_dir)
    monkeypatch.setattr(backup_service, "BACKUPS_DIR", fake_backups_dir)

    ActivityService(session).create_activity(
        title="테스트 활동", activity_type=ActivityType.SEMINAR, date_start=date(2026, 1, 1),
    )
    session.commit()

    backup_path = backup_service.create_backup()
    assert backup_path.exists()
    assert backup_path.parent == fake_backups_dir


def test_list_backups_sorted_newest_first(tmp_path, monkeypatch):
    import time
    fake_backups_dir = tmp_path / "backups"
    fake_backups_dir.mkdir()
    monkeypatch.setattr(backup_service, "BACKUPS_DIR", fake_backups_dir)

    old = fake_backups_dir / "uga_backup_20260101_000000.db"
    old.write_bytes(b"old")
    time.sleep(0.01)
    new = fake_backups_dir / "uga_backup_20260201_000000.db"
    new.write_bytes(b"new")

    backups = backup_service.list_backups()
    assert backups[0].name == new.name  # 최신이 먼저


def test_format_backup_label_readable(tmp_path):
    path = tmp_path / "uga_backup_20260315_143000.db"
    path.write_bytes(b"x" * 2048)
    label = backup_service.format_backup_label(path)
    assert "2026-03-15" in label
    assert "KB" in label
