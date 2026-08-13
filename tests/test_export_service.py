"""
tests/test_export_service.py

Markdown/PDF export가 실제 파일을 만들고, 그 안에 핵심 정보(제목, STAR,
카테고리, 성장 연결)가 포함되는지 검증합니다.
PDF는 내용을 텍스트로 직접 읽기 어려우므로, "파일이 정상적으로 생성되고
크기가 0보다 큰지"까지만 확인합니다 (실제 렌더링 품질은 개발 중 스크린샷으로 확인).
"""

import os
from datetime import date

from models.activity import ActivityType, ActivityStatus
from services.activity_service import ActivityService
from services.growth_link_service import GrowthLinkService
from services.export_service import ExportService


def _make_rich_activity(session):
    """STAR, 태그, 카테고리, Reflection, 성장 연결까지 다 채워진 활동을 만듭니다."""
    activity_service = ActivityService(session)
    a1 = activity_service.create_activity(
        title="교내 창업 공모전", activity_type=ActivityType.CONTEST,
        date_start=date(2026, 3, 1), status=ActivityStatus.DONE, importance=5,
        purpose="팀 프로젝트 경험", content="4인 팀으로 기획부터 발표까지 진행",
        category_names=["협업", "도전"], tag_names=["공모전"],
        star_situation="상황", star_task="과제", star_action="행동", star_result="결과",
    )
    a2 = activity_service.create_activity(
        title="다음 프로젝트", activity_type=ActivityType.PROJECT, date_start=date(2026, 4, 1),
    )
    GrowthLinkService(session).link_activities(a1.id, a2.id, reason="테스트 연결")
    session.refresh(a1)
    return a1


def test_export_to_markdown_contains_key_info(session, tmp_path, monkeypatch):
    import config
    monkeypatch.setattr(config, "EXPORTS_DIR", tmp_path)
    # export_service.py는 모듈 로드 시점에 EXPORTS_DIR를 import해서 쓰므로,
    # 모듈 자체의 참조도 함께 바꿔줘야 몽키패치가 실제로 적용됩니다.
    import services.export_service as export_module
    monkeypatch.setattr(export_module, "EXPORTS_DIR", tmp_path)

    activity = _make_rich_activity(session)
    path = ExportService().export_to_markdown(activity)

    assert os.path.exists(path)
    content = open(path, encoding="utf-8").read()
    assert "교내 창업 공모전" in content
    assert "협업" in content and "도전" in content
    assert "Situation" in content
    assert "다음 프로젝트" in content  # 성장 연결이 반영되었는지


def test_export_to_pdf_creates_nonempty_file(session, tmp_path, monkeypatch):
    import config
    import services.export_service as export_module
    monkeypatch.setattr(config, "EXPORTS_DIR", tmp_path)
    monkeypatch.setattr(export_module, "EXPORTS_DIR", tmp_path)

    activity = _make_rich_activity(session)
    path = ExportService().export_to_pdf(activity)

    assert os.path.exists(path)
    assert os.path.getsize(path) > 1000  # 최소한 텍스트가 들어간 정상 크기의 PDF
