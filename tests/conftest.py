"""
tests/conftest.py

모든 테스트가 공유하는 fixture를 정의합니다. 가장 중요한 건 `session` fixture인데,
실제 사용자 DB(database/uga.db)를 절대 건드리지 않도록 테스트마다 완전히
새로운 임시 SQLite 파일을 만들어서 씁니다 (테스트가 끝나면 자동으로 지워집니다).

pytest는 이 파일을 자동으로 찾아서 로드하므로, 각 테스트 파일에서
따로 import하지 않아도 아래 fixture들을 함수 인자로 바로 받아 쓸 수 있습니다.
"""

import sys
from pathlib import Path

# tests/ 폴더에서 실행해도 uga/ 패키지들을 import할 수 있도록 경로를 추가합니다.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest

from database import db_session
from models.base import Base


@pytest.fixture()
def session(tmp_path):
    """테스트 하나마다 완전히 새로운 임시 SQLite DB에 연결된 세션을 만들어줍니다."""
    db_path = tmp_path / "test_uga.db"
    db_session.configure(f"sqlite:///{db_path}")
    Base.metadata.create_all(bind=db_session.engine)

    # 기본 카테고리 시드 (실제 앱의 init_db()와 동일한 동작을 테스트에서도 재현)
    from services.category_service import CategoryService

    s = db_session.SessionLocal()
    try:
        CategoryService(s).ensure_default_categories()
    finally:
        s.close()

    test_session = db_session.SessionLocal()
    try:
        yield test_session
    finally:
        test_session.close()
