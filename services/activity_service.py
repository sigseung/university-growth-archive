"""
services/activity_service.py

Repository가 'DB에 어떻게 저장하는지'를 담당한다면,
Service는 '어떤 규칙으로 데이터를 다룰지'를 담당합니다.

예시:
    - "태그는 콤마로 구분된 문자열로 입력받아 Tag 객체들로 변환한다"
    - "대시보드에 필요한 통계 숫자를 계산한다"

ViewModel은 절대 Repository를 직접 호출하지 않고, 항상 이 Service를 거칩니다.
"""

from datetime import date

from sqlalchemy.orm import Session

from models.activity import Activity, ActivityStatus, ActivityType
from models.tag import Tag
from repositories.activity_repository import ActivityRepository


class ActivityService:
    def __init__(self, session: Session):
        self.session = session
        self.repo = ActivityRepository(session)

    # ---------- 생성/수정 ----------

    def create_activity(
        self,
        title: str,
        activity_type: ActivityType,
        date_start: date,
        status: ActivityStatus = ActivityStatus.PLANNED,
        date_end: date | None = None,
        location: str | None = None,
        organizer: str | None = None,
        importance: int = 3,
        purpose: str | None = None,
        content: str | None = None,
        tag_names: list[str] | None = None,
        goal_id: int | None = None,
    ) -> Activity:
        """새 활동을 만듭니다. 제목과 최소 정보만 있으면 저장 가능하게 해서
        '일단 빠르게 기록하고 나중에 상세 페이지에서 채워넣는' 사용 흐름을 지원합니다."""

        if not title or not title.strip():
            raise ValueError("활동 제목은 비어있을 수 없습니다.")
        if not (1 <= importance <= 5):
            raise ValueError("중요도는 1~5 사이여야 합니다.")

        activity = Activity(
            title=title.strip(),
            activity_type=activity_type,
            status=status,
            date_start=date_start,
            date_end=date_end,
            location=location,
            organizer=organizer,
            importance=importance,
            purpose=purpose,
            content=content,
            goal_id=goal_id,
        )

        if tag_names:
            activity.tags = self._resolve_tags(tag_names)

        return self.repo.create(activity)

    def update_activity(self, activity_id: int, **fields) -> Activity:
        activity = self.repo.get_by_id(activity_id)
        if activity is None:
            raise ValueError(f"id={activity_id} 활동을 찾을 수 없습니다.")

        tag_names = fields.pop("tag_names", None)
        for key, value in fields.items():
            if hasattr(activity, key):
                setattr(activity, key, value)

        if tag_names is not None:
            activity.tags = self._resolve_tags(tag_names)

        return self.repo.update(activity)

    def delete_activity(self, activity_id: int) -> bool:
        return self.repo.delete(activity_id)

    # ---------- 조회 ----------

    def get_activity(self, activity_id: int) -> Activity | None:
        return self.repo.get_by_id(activity_id)

    def list_activities(self) -> list[Activity]:
        return self.repo.get_all()

    def search_activities(self, keyword: str) -> list[Activity]:
        if not keyword or not keyword.strip():
            return self.list_activities()
        return self.repo.search(keyword.strip())

    def get_upcoming_activities(self, limit: int = 5) -> list[Activity]:
        return self.repo.get_upcoming()[:limit]

    # ---------- 대시보드용 통계 ----------

    def get_dashboard_stats(self) -> dict:
        """대시보드 상단 카드(전체 활동/참여완료/참여예정)에 필요한 숫자를 계산합니다."""
        return {
            "total": self.repo.count_all(),
            "done": self.repo.count_by_status(ActivityStatus.DONE),
            "upcoming": self.repo.count_by_status(ActivityStatus.PLANNED),
        }

    def get_this_month_activities(self) -> list[Activity]:
        today = date.today()
        return [
            a for a in self.list_activities()
            if a.date_start.year == today.year and a.date_start.month == today.month
        ]

    # ---------- 내부 헬퍼 ----------

    def _resolve_tags(self, tag_names: list[str]) -> list[Tag]:
        """태그 이름 목록을 받아, 이미 있는 태그는 재사용하고
        없는 태그는 새로 만들어서 Tag 객체 리스트로 돌려줍니다."""
        tags = []
        for raw_name in tag_names:
            name = raw_name.strip()
            if not name:
                continue
            existing = self.session.query(Tag).filter_by(name=name).first()
            tags.append(existing if existing else Tag(name=name))
        return tags
