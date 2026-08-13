"""
ai/prompts/star_prompt.py

활동 정보를 바탕으로 STAR(Situation/Task/Action/Result) 초안을
JSON으로 생성하도록 요청하는 프롬프트를 만듭니다.
"""

from models.activity import Activity


def build_star_prompt(activity: Activity) -> tuple[str, str]:
    system_prompt = (
        "너는 대학생의 자기소개서/면접 준비를 돕는 도우미다. 주어진 활동 정보를 "
        "STAR 기법(Situation-Task-Action-Result)으로 재구성하라. "
        "반드시 아래 형식의 순수 JSON 객체 하나만 답하라. 다른 설명은 절대 포함하지 마라.\n"
        '{"situation": "상황 (1~2문장)", "task": "과제/목표 (1~2문장)", '
        '"action": "행동 (2~3문장)", "result": "결과 (1~2문장)"}'
    )
    user_prompt = (
        f"활동명: {activity.title}\n"
        f"종류: {activity.activity_type.value}\n"
        f"참여 목적: {activity.purpose or '(작성 안 함)'}\n"
        f"활동 내용: {activity.content or '(작성 안 함)'}\n"
        f"새롭게 배운 기술: {activity.new_skills or '(작성 안 함)'}\n\n"
        "정보가 부족한 항목은 활동명과 종류를 참고해 자연스럽게 추론해서 채워줘. "
        "단, 사실이 아닌 수치나 성과를 지어내지는 마."
    )
    return system_prompt, user_prompt
