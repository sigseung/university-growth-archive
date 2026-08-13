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

# echo=False: SQL 쿼리 로그를 끔. 디버깅하고 싶을 때 True로 바꾸면
# 실행되는 모든 SQL문이 콘솔에 출력됩니다.
engine = create_engine(DATABASE_URL, echo=False)

# SessionLocal: 세션을 찍어내는 '공장(factory)'.
# 매번 SessionLocal()을 호출할 때마다 새로운 세션이 만들어집니다.
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def init_db() -> None:
    """앱 최초 실행 시 한 번 호출해서 모든 테이블을 생성합니다.
    이미 테이블이 있으면 아무 일도 하지 않습니다 (create_all의 기본 동작)."""
    # models 패키지를 import해야 모든 모델 클래스가 Base.metadata에 등록됩니다.
    import models  # noqa: F401  (등록 목적의 import이므로 사용하지 않아도 필요함)

    Base.metadata.create_all(bind=engine)


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
