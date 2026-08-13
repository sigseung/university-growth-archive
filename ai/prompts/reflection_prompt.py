"""
ai/prompts/reflection_prompt.py

활동 정보를 바탕으로 Reflection(느낀 점 / 앞으로 할 행동) 초안을
JSON으로 생성하도록 요청하는 프롬프트를 만듭니다.

모든 prompt 모듈은 동일한 형태를 따릅니다:
    build_xxx_prompt(...) -> (system_prompt: str, user_prompt: str)
이렇게 통일해두면 services/ai_content_service.py에서 어떤 prompt든
똑같은 방식(AIClient().complete(system, user))으로 호출할 수 있습니다.
"""

from models.activity import Activity


def build_reflection_prompt(activity: Activity) -> tuple[str, str]:
    system_prompt = (
        "너는 대학생의 활동 기록을 바탕으로 회고(reflection) 초안을 도와주는 도우미다. "
        "반드시 아래 형식의 순수 JSON 객체 하나만 답하라. 다른 설명이나 마크다운 코드블록은 절대 포함하지 마라.\n"
        '{"learned": "느낀 점 (2~3문장)", "next_action": "앞으로 할 행동 (2~3문장)"}'
    )
    user_prompt = (
        f"활동명: {activity.title}\n"
        f"종류: {activity.activity_type.value}\n"
        f"날짜: {activity.date_start}\n"
        f"참여 목적: {activity.purpose or '(작성 안 함)'}\n"
        f"활동 내용: {activity.content or '(작성 안 함)'}\n\n"
        "위 활동을 바탕으로 대학생 1인칭 시점의 자연스러운 한국어 회고 초안을 작성해줘."
    )
    return system_prompt, user_prompt
