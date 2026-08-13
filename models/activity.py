"""
models/activity.py

Activity(활동)는 UGA 전체 시스템의 중심이 되는 테이블입니다.
박람회, 세미나, 프로젝트, 공모전 등 대학생활의 모든 경험이
이 테이블의 한 행(row)으로 기록됩니다.

V1 범위:
    - 기본 필드(제목/날짜/장소/주최/종류/상태/중요도)
    - Reflection, Attachment, Tag 와의 관계(relationship)

V1 이후(V2~)에 추가될 예정인 필드는 일부러 지금 넣지 않았습니다.
  (Goal 연결, Category 연결, GrowthLink, STAR 필드 등)
  → 이유: V1에서는 "활동을 기록하고 목록/상세를 보는 것"에만 집중하고,
     기능이 늘어날 때마다 마이그레이션 개념을 연습하듯 컬럼을 추가합니다.
     (설계 문서에는 이미 전체 스키마가 정리되어 있으니 나중에 그대로 확장하면 됩니다.)
"""

import enum
from datetime import date, datetime

from sqlalchemy import String, Text, Date, DateTime, Integer, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base


class ActivityType(str, enum.Enum):
    """활동 종류. DB에는 문자열(예: 'FAIR')로 저장되고,
    파이썬 코드에서는 ActivityType.FAIR 처럼 안전하게 사용합니다."""
    FAIR = "박람회"
    SEMINAR = "세미나"
    PROJECT = "프로젝트"
    CONTEST = "공모전"
    LAB = "연구실"
    CERTIFICATE = "자격증"
    EXTERNAL = "대외활동"
    CLUB = "동아리"
    VOLUNTEER = "봉사"
    READING = "독서"
    COURSE_PROJECT = "수업프로젝트"
    EXERCISE = "운동"
    ETC = "기타"


class ActivityStatus(str, enum.Enum):
    """활동 진행 상태."""
    PLANNED = "예정"
    ONGOING = "진행중"
    DONE = "완료"


class Activity(Base):
    __tablename__ = "activities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # --- 기본 정보 ---
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    activity_type: Mapped[ActivityType] = mapped_column(
        Enum(ActivityType), nullable=False, default=ActivityType.ETC
    )
    status: Mapped[ActivityStatus] = mapped_column(
        Enum(ActivityStatus), nullable=False, default=ActivityStatus.PLANNED
    )
    date_start: Mapped[date] = mapped_column(Date, nullable=False)
    date_end: Mapped[date | None] = mapped_column(Date, nullable=True)
    location: Mapped[str | None] = mapped_column(String(200), nullable=True)
    organizer: Mapped[str | None] = mapped_column(String(200), nullable=True)
    importance: Mapped[int] = mapped_column(Integer, default=3)  # 1~5

    # --- 상세 내용 (활동 상세 페이지에서 채워짐) ---
    purpose: Mapped[str | None] = mapped_column(Text, nullable=True)       # 참여 목적
    content: Mapped[str | None] = mapped_column(Text, nullable=True)      # 활동 내용
    visited_companies: Mapped[str | None] = mapped_column(Text, nullable=True)
    qna: Mapped[str | None] = mapped_column(Text, nullable=True)
    new_skills: Mapped[str | None] = mapped_column(Text, nullable=True)
    new_roles: Mapped[str | None] = mapped_column(Text, nullable=True)
    related_link: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # --- 메타 ---
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, onupdate=datetime.now
    )

    # --- 관계 (relationship) ---
    # cascade="all, delete-orphan": 활동을 삭제하면 딸린 Reflection/Attachment도 함께 삭제
    reflections: Mapped[list["Reflection"]] = relationship(
        back_populates="activity", cascade="all, delete-orphan"
    )
    attachments: Mapped[list["Attachment"]] = relationship(
        back_populates="activity", cascade="all, delete-orphan"
    )
    tags: Mapped[list["Tag"]] = relationship(
        secondary="activity_tags", back_populates="activities"
    )

    def __repr__(self) -> str:
        return f"<Activity id={self.id} title={self.title!r} type={self.activity_type}>"
