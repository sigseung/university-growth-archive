"""
repositories/activity_repository.py

Activity 테이블에 대한 CRUD(Create/Read/Update/Delete)만 담당합니다.

★ 규칙: 이 파일에는 '비즈니스 로직'을 넣지 않습니다.
   예를 들어 "중요도가 4 이상인 것만 대시보드에 보여준다" 같은 규칙은
   여기가 아니라 services/activity_service.py 에 있어야 합니다.
   이 파일은 순수하게 "DB에 저장한다 / DB에서 가져온다"만 합니다.

이렇게 분리해두면 나중에 SQLite에서 PostgreSQL로 바꾸거나,
테스트에서 가짜(mock) 데이터로 바꿔치기하기 쉬워집니다.
"""

from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from models.activity import Activity, ActivityStatus, ActivityType


class ActivityRepository:
    """생성자에서 session을 하나 받아서, 그 세션으로만 작업합니다.
    (세션을 이 클래스 내부에서 새로 만들지 않는 이유: 하나의 트랜잭션 안에서
     여러 Repository를 함께 써야 할 때가 있기 때문입니다.)"""

    def __init__(self, session: Session):
        self.session = session

    def create(self, activity: Activity) -> Activity:
        self.session.add(activity)
        self.session.commit()
        self.session.refresh(activity)  # DB가 채운 id 등을 다시 읽어옴
        return activity

    def get_by_id(self, activity_id: int) -> Activity | None:
        return self.session.get(Activity, activity_id)

    def get_all(self) -> list[Activity]:
        stmt = select(Activity).order_by(Activity.date_start.desc())
        return list(self.session.scalars(stmt).all())

    def get_by_status(self, status: ActivityStatus) -> list[Activity]:
        stmt = (
            select(Activity)
            .where(Activity.status == status)
            .order_by(Activity.date_start.desc())
        )
        return list(self.session.scalars(stmt).all())

    def get_by_type(self, activity_type: ActivityType) -> list[Activity]:
        stmt = (
            select(Activity)
            .where(Activity.activity_type == activity_type)
            .order_by(Activity.date_start.desc())
        )
        return list(self.session.scalars(stmt).all())

    def get_upcoming(self, today: date | None = None) -> list[Activity]:
        """오늘 이후의 예정된 활동들 (일정 위젯 등에서 사용)."""
        today = today or date.today()
        stmt = (
            select(Activity)
            .where(Activity.date_start >= today)
            .order_by(Activity.date_start.asc())
        )
        return list(self.session.scalars(stmt).all())

    def search(self, keyword: str) -> list[Activity]:
        """제목/내용/주최/장소에 키워드가 포함된 활동을 검색합니다.
        (V2에서 태그/기업/기술 검색까지 확장 예정)"""
        like_pattern = f"%{keyword}%"
        stmt = select(Activity).where(
            Activity.title.like(like_pattern)
            | Activity.content.like(like_pattern)
            | Activity.organizer.like(like_pattern)
            | Activity.location.like(like_pattern)
        )
        return list(self.session.scalars(stmt).all())

    def update(self, activity: Activity) -> Activity:
        # SQLAlchemy 세션이 이미 activity 객체를 추적(track)하고 있다면
        # commit만으로 변경사항이 반영됩니다.
        self.session.commit()
        self.session.refresh(activity)
        return activity

    def delete(self, activity_id: int) -> bool:
        activity = self.get_by_id(activity_id)
        if activity is None:
            return False
        self.session.delete(activity)
        self.session.commit()
        return True

    def count_all(self) -> int:
        return len(self.get_all())

    def count_by_status(self, status: ActivityStatus) -> int:
        return len(self.get_by_status(status))
