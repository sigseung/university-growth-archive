"""
ai/prompts/interview_prompt.py

활동 하나를 근거로 예상 면접 질문 + 꼬리질문 + 모범답변을
JSON 리스트로 생성하도록 요청하는 프롬프트를 만듭니다.
"""

from models.activity import Activity


def build_interview_prompt(activity: Activity) -> tuple[str, str]:
    system_prompt = (
        "너는 대학생 채용 면접관이다. 주어진 활동을 근거로 예상 질문 3개를 만들어라. "
        "각 질문에는 꼬리질문 1개와, 지원자가 참고할 수 있는 모범답변 예시를 함께 만들어라. "
        "반드시 아래 형식의 순수 JSON 객체 하나만 답하라. 다른 설명은 절대 포함하지 마라.\n"
        '{"items": [{"question": "...", "follow_up": "...", "model_answer": "..."}, '
        '... (정확히 3개)]}'
    )
    star_text = ""
    if any([activity.star_situation, activity.star_task, activity.star_action, activity.star_result]):
        star_text = (
            f"\nSTAR - Situation: {activity.star_situation or ''} / "
            f"Task: {activity.star_task or ''} / Action: {activity.star_action or ''} / "
            f"Result: {activity.star_result or ''}"
        )

    user_prompt = (
        f"활동명: {activity.title}\n"
        f"종류: {activity.activity_type.value}\n"
        f"활동 내용: {activity.content or '(작성 안 함)'}"
        f"{star_text}\n\n"
        "위 활동을 바탕으로 면접에서 나올 법한 질문과 모범답변을 만들어줘."
    )
    return system_prompt, user_prompt
