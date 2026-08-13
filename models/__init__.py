"""
models/__init__.py

이 파일이 하는 일은 딱 하나입니다:
다른 모듈들이 매번 'from models.activity import Activity' 처럼
긴 경로를 쓰지 않고 'from models import Activity' 로 쓸 수 있게 해줍니다.

또한 SQLAlchemy가 create_all()을 호출할 때 모든 모델 클래스가
'한 번은 import 되어 있어야' Base.metadata에 등록됩니다.
이 파일에서 전부 import 해두면 database/db_session.py에서
'from models import *' 한 번으로 모든 테이블이 인식됩니다.
"""

from models.base import Base
from models.activity import Activity, ActivityType, ActivityStatus
from models.reflection import Reflection
from models.attachment import Attachment, AttachmentType
from models.tag import Tag, activity_tags
from models.goal import Goal, PeriodType
from models.schedule import Schedule, ScheduleType

__all__ = [
    "Base",
    "Activity",
    "ActivityType",
    "ActivityStatus",
    "Reflection",
    "Attachment",
    "AttachmentType",
    "Tag",
    "activity_tags",
    "Goal",
    "PeriodType",
    "Schedule",
    "ScheduleType",
]
