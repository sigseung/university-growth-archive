"""
analytics/stats_calculator.py

Activity 리스트를 받아서 '숫자로 집계'하는 순수 함수들만 모아둡니다.
여기 있는 함수들은 Matplotlib이나 CustomTkinter를 전혀 모릅니다.
(집계 로직과 "그걸 어떻게 그릴지"를 분리해두면, 나중에 그래프 라이브러리를
바꾸거나 같은 숫자를 표(테이블)로도 보여주고 싶을 때 이 파일을 그대로 재사용할 수 있습니다.)
"""

from collections import Counter, defaultdict
from datetime import date as _date

from models.activity import Activity, ActivityStatus


def count_by_year(activities: list[Activity]) -> dict[int, int]:
    """{연도: 활동 수}. 커리어 타임라인의 '연도별 활동' 통계."""
    counter: Counter = Counter(a.date_start.year for a in activities)
    return dict(sorted(counter.items()))


def count_by_month(activities: list[Activity], year: int) -> dict[int, int]:
    """특정 연도의 {월(1~12): 활동 수}. 월이 비어있어도 0으로 채워서 반환합니다
    (그래프에서 빈 달이 그냥 생략되면 흐름을 오해하기 쉽기 때문)."""
    counter: Counter = Counter(
        a.date_start.month for a in activities if a.date_start.year == year
    )
    return {month: counter.get(month, 0) for month in range(1, 13)}


def count_by_type(activities: list[Activity]) -> dict[str, int]:
    """{활동 종류: 개수}. 파이 차트(활동 종류별 비율)에 사용."""
    counter: Counter = Counter(a.activity_type.value for a in activities)
    # 개수가 많은 순으로 정렬해서, 범례가 자연스럽게 중요한 것부터 나열되게 함
    return dict(counter.most_common())


def most_active_type(activities: list[Activity]) -> str | None:
    """가장 많이 참여한 활동 종류 하나."""
    counts = count_by_type(activities)
    if not counts:
        return None
    return max(counts, key=counts.get)


def growth_trend_by_month(activities: list[Activity]) -> list[tuple[str, int]]:
    """전체 기간에 걸친 (YYYY-MM, 누적 활동 수) 리스트. '성장 추이' 라인 차트용.
    대시보드의 작은 스파크라인이 아니라, 통계 화면의 큰 추이 그래프에 사용됩니다."""
    monthly_counts: dict[str, int] = defaultdict(int)
    for a in activities:
        key = f"{a.date_start.year}-{a.date_start.month:02d}"
        monthly_counts[key] += 1

    sorted_keys = sorted(monthly_counts.keys())
    result = []
    cumulative = 0
    for key in sorted_keys:
        cumulative += monthly_counts[key]
        result.append((key, cumulative))
    return result


def completion_summary(activities: list[Activity]) -> dict[str, int]:
    """상태별(완료/진행중/예정) 개수. 통계 화면 상단 요약 카드용."""
    counter: Counter = Counter(a.status.value for a in activities)
    return {
        status.value: counter.get(status.value, 0) for status in ActivityStatus
    }


def build_summary_text(activities: list[Activity]) -> str:
    """AI 성장 분석 프롬프트에 넣을 '사람이 읽기 좋은 통계 요약 텍스트'를 만듭니다.
    AI에게 표/딕셔너리를 그대로 주는 것보다, 문장 형태로 정리해서 주면
    더 안정적으로 분석 품질이 나옵니다."""
    if not activities:
        return "아직 기록된 활동이 없습니다."

    lines = [f"전체 활동 수: {len(activities)}개"]

    year_counts = count_by_year(activities)
    lines.append("연도별 활동 수: " + ", ".join(f"{y}년 {c}개" for y, c in year_counts.items()))

    type_counts = count_by_type(activities)
    top_types = list(type_counts.items())[:5]
    lines.append("활동 종류별 개수(상위 5개): " + ", ".join(f"{t} {c}개" for t, c in top_types))

    summary = completion_summary(activities)
    lines.append(f"상태별: 완료 {summary.get('완료', 0)}개, 진행중 {summary.get('진행중', 0)}개, 예정 {summary.get('예정', 0)}개")

    # 최근 6개월 활동 수 (증감 추세를 AI가 짚어줄 수 있도록)
    today = _date.today()
    recent_6m = [
        a for a in activities
        if (today.year - a.date_start.year) * 12 + (today.month - a.date_start.month) <= 6
        and a.date_start <= today
    ]
    lines.append(f"최근 6개월 내 활동 수: {len(recent_6m)}개")

    # 카테고리(자소서 분류)별 개수도 포함 — "협업 경험이 부족합니다" 같은 분석에 필요
    category_counter: Counter = Counter()
    for a in activities:
        for c in a.categories:
            category_counter[c.name] += 1
    if category_counter:
        lines.append(
            "자기소개서 분류별 개수: " + ", ".join(f"{name} {cnt}개" for name, cnt in category_counter.most_common())
        )

    return "\n".join(lines)
