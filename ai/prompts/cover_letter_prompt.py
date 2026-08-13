"""
ai/prompts/cover_letter_prompt.py

특정 자기소개서 카테고리(예: '협업')로 분류된 활동들을 모아서,
그 역량을 보여주는 자기소개서 문단 초안을 생성하는 프롬프트를 만듭니다.
"""

from models.activity import Activity


def build_cover_letter_prompt(activities: list[Activity], category_name: str) -> tuple[str, str]:
    system_prompt = (
        f"너는 대학생 자기소개서 작성을 돕는 도우미다. "
        f"주어진 여러 경험을 종합해서 '{category_name}' 역량을 보여주는 "
        "자기소개서 문단을 한국어로 작성하라. "
        "순수 텍스트로만 답하고, 마크다운이나 따옴표로 감싸지 마라. "
        "400자 내외, 구체적 경험 위주로, 과장하지 말고 사실에 기반해서 작성하라."
    )

    activity_lines = "\n".join(
        f"- {a.title} ({a.date_start}): {a.content or a.purpose or '(상세 내용 없음)'}"
        for a in activities
    )
    user_prompt = (
        f"다음은 '{category_name}' 카테고리로 분류된 활동들이다:\n{activity_lines}\n\n"
        "이 경험들을 하나의 자연스러운 자기소개서 문단으로 작성해줘."
    )
    return system_prompt, user_prompt
