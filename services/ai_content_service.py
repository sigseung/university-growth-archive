"""
services/ai_content_service.py

버튼 하나로 AI가 초안을 만들어주는 기능들을 모아둔 곳입니다.
    - Reflection 초안 (느낀 점 / 앞으로 할 행동)
    - STAR 초안 (Situation/Task/Action/Result)
    - 자기소개서 문단 (카테고리별)
    - 면접 예상 질문/모범답변 (활동별, InterviewQA로 저장까지)

AI 응답은 항상 "JSON 문자열"로 오도록 프롬프트에서 강제하고 있지만,
모델이 가끔 형식을 어길 수 있으므로 이 파일에서 파싱 실패를 잡아서
사용자에게 이해하기 쉬운 메시지로 바꿔줍니다.
"""

import json

from sqlalchemy.orm import Session

from ai.ai_client import AIClient
from ai.prompts.reflection_prompt import build_reflection_prompt
from ai.prompts.star_prompt import build_star_prompt
from ai.prompts.cover_letter_prompt import build_cover_letter_prompt
from ai.prompts.interview_prompt import build_interview_prompt
from models.activity import Activity
from repositories.interview_qa_repository import InterviewQARepository


def _parse_json_response(raw_text: str) -> dict:
    """AI 응답에서 JSON을 파싱합니다. 모델이 코드블록(```json ... ```)으로
    감싸서 답하는 경우가 종종 있어서, 그 경우도 함께 처리합니다."""
    text = raw_text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"AI 응답을 해석할 수 없습니다. 다시 시도해주세요. ({e})")


class AIContentService:
    def __init__(self, session: Session):
        self.session = session
        self.interview_repo = InterviewQARepository(session)

    def generate_reflection(self, activity: Activity) -> dict:
        """반환: {"learned": str, "next_action": str}"""
        system_prompt, user_prompt = build_reflection_prompt(activity)
        raw = AIClient().complete(system_prompt, user_prompt, max_tokens=400)
        data = _parse_json_response(raw)
        if "learned" not in data or "next_action" not in data:
            raise ValueError("AI 응답 형식이 예상과 다릅니다. 다시 시도해주세요.")
        return data

    def generate_star(self, activity: Activity) -> dict:
        """반환: {"situation", "task", "action", "result"}"""
        system_prompt, user_prompt = build_star_prompt(activity)
        raw = AIClient().complete(system_prompt, user_prompt, max_tokens=500)
        data = _parse_json_response(raw)
        required = {"situation", "task", "action", "result"}
        if not required.issubset(data.keys()):
            raise ValueError("AI 응답 형식이 예상과 다릅니다. 다시 시도해주세요.")
        return data

    def generate_cover_letter_paragraph(self, activities: list[Activity], category_name: str) -> str:
        if not activities:
            raise ValueError("이 카테고리로 분류된 활동이 없습니다.")
        system_prompt, user_prompt = build_cover_letter_prompt(activities, category_name)
        return AIClient().complete(system_prompt, user_prompt, max_tokens=600).strip()

    def generate_and_save_interview_qa(self, activity: Activity) -> list:
        """AI로 면접 질문 3개를 생성하고, 바로 InterviewQA 테이블에 저장까지 합니다."""
        system_prompt, user_prompt = build_interview_prompt(activity)
        raw = AIClient().complete(system_prompt, user_prompt, max_tokens=900)
        data = _parse_json_response(raw)
        items = data.get("items", [])
        if not items:
            raise ValueError("AI가 질문을 생성하지 못했습니다. 다시 시도해주세요.")

        saved = []
        for item in items:
            qa = self.interview_repo.create(
                activity_id=activity.id,
                question=item.get("question", "").strip(),
                follow_up_question=(item.get("follow_up") or "").strip() or None,
                model_answer=(item.get("model_answer") or "").strip() or None,
                is_ai_generated=True,
            )
            saved.append(qa)
        return saved
