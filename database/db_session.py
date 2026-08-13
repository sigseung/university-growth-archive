"""
database/db_session.py

SQLAlchemy의 '엔진(Engine)'과 '세션(Session)'을 만드는 곳입니다.

- Engine: DB 파일과의 실제 연결을 관리하는 객체 (앱 전체에서 1개만 존재)
- Session: 하나의 '작업 단위(트랜잭션)'를 나타내는 객체
           (요청 하나당 세션 하나를 열고, 끝나면 닫는 것이 원칙)

Repository들은 이 파일의 get_session()을 통해서만 DB에 접근합니다.
"""

from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from config import DATABASE_URL
from models.base import Base


def _build_engine_and_sessionmaker(database_url: str):
    # echo=False: SQL 쿼리 로그를 끔. 디버깅하고 싶을 때 True로 바꾸면
    # 실행되는 모든 SQL문이 콘솔에 출력됩니다.
    new_engine = create_engine(database_url, echo=False)
    new_session_local = sessionmaker(bind=new_engine, autoflush=False, autocommit=False)
    return new_engine, new_session_local


engine, SessionLocal = _build_engine_and_sessionmaker(DATABASE_URL)


def configure(database_url: str) -> None:
    """engine/SessionLocal을 다른 DB로 다시 연결합니다.

    두 가지 경우에 씁니다:
    1) 테스트 코드 (tests/conftest.py)에서 실제 사용자 DB 대신
       임시 SQLite 파일을 쓰도록 바꿔치기할 때.
    2) 백업 복원 후, 새로 열리는 세션이 복원된 파일을 바라보게 할 때.

    기존 engine이 연결을 물고 있으면 파일 교체가 막힐 수 있어서,
    새로 만들기 전에 기존 연결을 정리(dispose)합니다."""
    global engine, SessionLocal
    engine.dispose()
    engine, SessionLocal = _build_engine_and_sessionmaker(database_url)


def init_db() -> None:
    """앱 최초 실행 시 한 번 호출해서 모든 테이블을 생성합니다.
    이미 테이블이 있으면 아무 일도 하지 않습니다 (create_all의 기본 동작).
    테이블 생성 후에는 자기소개서 분류 기본 9종(Category)도 없으면 심어둡니다."""
    # models 패키지를 import해야 모든 모델 클래스가 Base.metadata에 등록됩니다.
    import models  # noqa: F401  (등록 목적의 import이므로 사용하지 않아도 필요함)

    Base.metadata.create_all(bind=engine)

    # 순환 import를 피하기 위해 함수 안에서 import합니다.
    # (services -> repositories -> models -> ... 로 이어지는 의존 체인이
    #  database 모듈을 다시 참조하지 않도록 이 함수 내부로 한정)
    from services.category_service import CategoryService

    session = SessionLocal()
    try:
        CategoryService(session).ensure_default_categories()
    finally:
        session.close()


@contextmanager
def get_session():
    """with get_session() as session: 형태로 사용하는 세션 컨텍스트 매니저.

    사용 예:
        with get_session() as session:
            session.add(activity)
            session.commit()

    이렇게 하면 코드 블록이 끝날 때 세션이 자동으로 닫히고,
    에러가 나면 자동으로 rollback 되어 DB가 이상한 상태로 남지 않습니다.
    """
    session: Session = SessionLocal()
    try:
        yield session
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
