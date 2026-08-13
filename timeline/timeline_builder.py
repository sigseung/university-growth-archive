"""
timeline/timeline_builder.py

Activity + GrowthLink 리스트를 받아서, 타임라인 화면이 그리기 편한
형태(연도별로 묶고, 각 활동에 딸린 outgoing_link 정보를 함께 정리)로 가공합니다.
View는 이 함수가 만들어준 구조를 그대로 그리기만 하면 되도록 해서,
"어떻게 그릴지"와 "무엇을 그릴지"를 분리했습니다.
"""

from collections import defaultdict

from models.activity import Activity


def group_by_year(activities: list[Activity]) -> dict[int, list[Activity]]:
    """{연도: [그 해의 활동들 (날짜 오름차순)]}"""
    by_year: dict[int, list[Activity]] = defaultdict(list)
    for a in activities:
        by_year[a.date_start.year].append(a)

    for year in by_year:
        by_year[year].sort(key=lambda a: a.date_start)

    # 연도는 오래된 것부터 보여주는 게 "성장 흐름"을 읽기에 자연스럽습니다.
    return dict(sorted(by_year.items()))


# 활동 종류별 색상. views/components/card.py의 배지 색상과 통일감을 맞췄습니다.
TYPE_COLORS = {
    "박람회": "#F59E0B", "세미나": "#3B82F6", "프로젝트": "#10B981",
    "공모전": "#EF4444", "연구실": "#8B5CF6", "자격증": "#06B6D4",
    "대외활동": "#EC4899", "동아리": "#F97316", "봉사": "#84CC16",
    "독서": "#6366F1", "수업프로젝트": "#14B8A6", "운동": "#F43F5E",
    "기타": "#6B7280",
}


def type_color(activity_type_value: str) -> str:
    return TYPE_COLORS.get(activity_type_value, "#6B7280")
