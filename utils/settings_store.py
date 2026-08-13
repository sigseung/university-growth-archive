"""
utils/settings_store.py

API 키처럼 "사용자마다 다르고, 코드에 하드코딩하면 안 되는" 값을 저장하는 곳입니다.
환경변수(OPENAI_API_KEY)로 설정하는 방법도 지원하지만, 초보자가 매번 환경변수를
설정하기는 번거로우므로 앱 안의 '설정' 화면에서 입력하면 로컬 JSON 파일에
저장해두고 다음 실행부터 자동으로 불러오는 방식도 함께 제공합니다.

★ 보안 참고: settings.json은 API 키가 평문으로 저장됩니다.
   그래서 config.py에서 이 파일이 있는 폴더를 .gitignore에 등록해서
   실수로 GitHub에 API 키가 올라가지 않도록 안내합니다 (README 참고).
"""

import json
from pathlib import Path

from config import BASE_DIR

_SETTINGS_PATH = BASE_DIR / "settings.json"


def _load_all() -> dict:
    if not _SETTINGS_PATH.exists():
        return {}
    try:
        return json.loads(_SETTINGS_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def _save_all(data: dict) -> None:
    _SETTINGS_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def get_setting(key: str, default: str | None = None) -> str | None:
    return _load_all().get(key, default)


def set_setting(key: str, value: str) -> None:
    data = _load_all()
    data[key] = value
    _save_all(data)


def get_openai_api_key() -> str | None:
    """우선순위: 환경변수(OPENAI_API_KEY) > 앱 설정 화면에서 저장한 값.
    환경변수를 우선하는 이유: 개발자가 터미널에서 실행할 때 매번 설정 화면을
    거치지 않고 바로 테스트할 수 있게 하기 위함입니다."""
    import os

    env_key = os.environ.get("OPENAI_API_KEY")
    if env_key:
        return env_key
    return get_setting("openai_api_key")


def set_openai_api_key(api_key: str) -> None:
    set_setting("openai_api_key", api_key)
