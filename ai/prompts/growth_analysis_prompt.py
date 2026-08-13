"""
ai/prompts/growth_analysis_prompt.py

전체 활동 통계 요약(텍스트)을 받아서, "성장 분석 + 다음 행동 추천" 리포트를
생성하도록 요청하는 프롬프트를 만듭니다.

설계 문서의 예시 문장들("최근 6개월 동안 AI 분야 활동이 크게 증가했습니다" 등)이
바로 이 프롬프트의 결과물이 지향하는 톤입니다.
"""


def build_growth_analysis_prompt(stats_summary: str) -> tuple[str, str]:
    system_prompt = (
        "너는 대학생 전담 커리어 코치다. 주어진 활동 통계를 분석해서 "
        "이 학생의 성장 패턴에 대한 인사이트와 다음 행동 추천을 한국어로 제시하라. "
        "5~7개의 짧은 문장으로, 각 줄은 하이픈(-)으로 시작하는 목록 형태로 작성하라. "
        "마크다운 헤더나 굵은 글씨는 쓰지 말고, 순수 텍스트 목록만 작성하라. "
        "근거 없는 수치나 사실을 지어내지 말고, 주어진 통계 안에서만 분석하라."
    )
    user_prompt = f"다음은 이 학생의 활동 통계다:\n\n{stats_summary}\n\n이를 바탕으로 성장 분석 리포트를 작성해줘."
    return system_prompt, user_prompt
