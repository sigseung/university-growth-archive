"""
ai/ai_client.py

OpenAI API를 직접 감싸는 유일한 파일입니다. 이 파일 밖에서는 아무도
'openai' 패키지를 직접 import하지 않습니다 (services/ai/analysis_service.py나
views/ 어디에서도). 이렇게 하나로 모아두면:
    - 나중에 OpenAI 말고 다른 LLM으로 바꾸고 싶을 때 이 파일만 고치면 됩니다.
    - API 키가 없을 때 "앱이 아예 죽는" 대신 "AI 기능만 못 쓴다"는
      명확한 예외(AIConfigError)로 처리해서 나머지 기능에 영향이 없게 합니다.
"""

from utils.settings_store import get_openai_api_key

# 실제로 호출할 모델. gpt-4o-mini 정도면 비용도 저렴하고 이 앱의 용도
# (짧은 요약/문장 생성)에는 충분합니다. 필요하면 나중에 바꾸기 쉽도록
# 상수로 분리해뒀습니다.
DEFAULT_MODEL = "gpt-4o-mini"


class AIConfigError(Exception):
    """API 키가 설정되지 않았을 때 발생. 이 예외를 View에서 잡아서
    '설정 화면에서 API 키를 입력해주세요' 같은 안내를 보여줘야 합니다."""
    pass


class AIRequestError(Exception):
    """API 키는 있지만 호출 자체가 실패했을 때 (네트워크 오류, 요금 초과 등)."""
    pass


class AIClient:
    def __init__(self, model: str = DEFAULT_MODEL):
        self.model = model

    def complete(self, system_prompt: str, user_prompt: str, max_tokens: int = 600) -> str:
        """system_prompt(역할 지시) + user_prompt(실제 요청)을 받아
        AI가 생성한 텍스트를 반환합니다. 실패하면 예외를 던집니다
        (호출하는 쪽에서 try/except로 감싸서 사용자에게 친절한 메시지를 보여줘야 함)."""
        api_key = get_openai_api_key()
        if not api_key:
            raise AIConfigError(
                "OpenAI API 키가 설정되지 않았습니다. '설정' 화면에서 API 키를 입력해주세요."
            )

        try:
            # openai 패키지를 함수 안에서 import하는 이유: API 키가 없는 환경(예:
            # AI 기능을 아예 안 쓰는 사용자)에서도 앱의 나머지 부분이 이 import
            # 실패 때문에 통째로 죽지 않도록, 실제로 필요한 순간에만 불러옵니다.
            from openai import OpenAI

            client = OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model=self.model,
                max_tokens=max_tokens,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )
            return response.choices[0].message.content.strip()
        except AIConfigError:
            raise
        except Exception as e:
            raise AIRequestError(f"AI 요청 중 오류가 발생했습니다: {e}") from e
