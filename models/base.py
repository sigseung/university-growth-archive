"""
models/base.py

모든 모델(Model)이 상속받는 SQLAlchemy Base 클래스를 정의합니다.
이 파일 하나만 두는 이유: 모든 모델이 '같은 Base'를 상속해야
SQLAlchemy가 테이블들을 하나의 메타데이터로 인식하고,
create_all() 한 번으로 모든 테이블을 생성할 수 있기 때문입니다.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """모든 ORM 모델의 공통 베이스 클래스."""
    pass
