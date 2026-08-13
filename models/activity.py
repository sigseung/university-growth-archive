"""
models/activity.py

Activity(활동)는 UGA 전체 시스템의 중심이 되는 테이블입니다.
박람회, 세미나, 프로젝트, 공모전 등 대학생활의 모든 경험이
이 테이블의 한 행(row)으로 기록됩니다.

V1 범위:
    - 기본 필드(제목/날짜/장소/주최/종류/상태/중요도)
    - Reflection, Attachment, Tag 와의 관계(relationship)

V2에서 추가된 것:
    - goal_id (Goal과의 N:1 연결. "이 활동은 어떤 목표를 위한 것인가")

V3에서 추가된 것:
    - categories (Category와의 N:M 연결. "이 활동은 자소서 어떤 항목에 쓸 수 있는가")

V4에서 추가된 것:
    - STAR 4필드 (Situation/Task/Action/Result) — 자기소개서/면접 답변의 기본 골격
    - outgoing_links / incoming_links (GrowthLink와의 관계. "이 활동이 어떤 다음
      행동으로 이어졌는가" / "이 활동은 어떤 활동 때문에 시작됐는가")

V5에서 추가된 것:
    - interview_qas (InterviewQA와의 1:N 관계. AI가 생성한 면접 예상질문 저장)
"""

import enum
from datetime import date, datetime

from sqlalchemy import String, Text, Date, DateTime, Integer, Enum, ForeignKey
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

    # --- STAR (V4): 자기소개서/면접 답변의 기본 골격 ---
    star_situation: Mapped[str | None] = mapped_column(Text, nullable=True)  # 상황
    star_task: Mapped[str | None] = mapped_column(Text, nullable=True)       # 과제/목표
    star_action: Mapped[str | None] = mapped_column(Text, nullable=True)     # 행동
    star_result: Mapped[str | None] = mapped_column(Text, nullable=True)     # 결과

    # --- 목표 연결 (V2) ---
    # 이 활동이 어떤 목표를 위해 한 것인지 (선택 사항)
    goal_id: Mapped[int | None] = mapped_column(ForeignKey("goals.id"), nullable=True)

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
    categories: Mapped[list["Category"]] = relationship(
        secondary="activity_categories", back_populates="activities"
    )
    goal: Mapped["Goal | None"] = relationship(back_populates="activities")

    # GrowthLink (V4): 이 활동에서 '출발하는' 연결과, 이 활동으로 '들어오는' 연결.
    # cascade="all, delete-orphan": 활동을 삭제하면 그 활동이 걸려있던 연결선도 함께 삭제
    outgoing_links: Mapped[list["GrowthLink"]] = relationship(
        foreign_keys="GrowthLink.from_activity_id",
        back_populates="from_activity", cascade="all, delete-orphan",
    )
    incoming_links: Mapped[list["GrowthLink"]] = relationship(
        foreign_keys="GrowthLink.to_activity_id",
        back_populates="to_activity", cascade="all, delete-orphan",
    )
    interview_qas: Mapped[list["InterviewQA"]] = relationship(
        back_populates="activity", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Activity id={self.id} title={self.title!r} type={self.activity_type}>"
