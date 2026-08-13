"""
utils/date_utils.py

날짜 형식 변환 등, 여러 View/Service에서 공통으로 쓰는
자잘한 날짜 관련 함수들을 모아둡니다.
"""

from datetime import date, datetime


def format_date_kr(d: date | None) -> str:
    """date 객체를 '2026년 3월 15일' 형식의 한국어 문자열로 변환."""
    if d is None:
        return "-"
    return f"{d.year}년 {d.month}월 {d.day}일"


def format_date_short(d: date | None) -> str:
    """date 객체를 'YYYY-MM-DD' 형식으로 변환. 입력창 표시용."""
    if d is None:
        return ""
    return d.strftime("%Y-%m-%d")


def parse_date_short(text: str) -> date:
    """'YYYY-MM-DD' 형식 문자열을 date 객체로 변환.
    형식이 틀리면 ValueError가 발생하며, 호출하는 쪽(View)에서
    사용자에게 '날짜 형식이 올바르지 않습니다' 같은 메시지를 보여줘야 합니다."""
    return datetime.strptime(text.strip(), "%Y-%m-%d").date()


def days_until(target: date) -> int:
    """오늘부터 target까지 남은 일수. 대시보드의 'D-3' 표시에 사용."""
    return (target - date.today()).days
