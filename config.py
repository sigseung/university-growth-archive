"""
config.py

프로젝트 전체에서 공유하는 설정값을 모아두는 파일입니다.
'경로를 코드 여기저기에 하드코딩하지 않는다'는 원칙을 지키기 위한 곳입니다.

★ PyInstaller 패키징 관련 중요 주의사항:
개발 중에는 Path(__file__).resolve().parent 가 이 프로젝트 폴더를 정확히
가리키지만, PyInstaller로 실행파일을 만들면 __file__은 압축 해제된
임시 내부 경로(예: _internal/ 안쪽)를 가리키게 됩니다. 이 상태에서 그대로
쓰면 사용자의 데이터베이스/백업/첨부파일이 실행파일과 상관없는 임시 위치에
생기고, 앱을 껐다 켜면 그 위치가 또 바뀔 수도 있어서 데이터가 사라진
것처럼 보이는 심각한 문제가 됩니다. 그래서 sys.frozen(PyInstaller가
설정해주는 플래그)을 확인해서, 패키징된 상태에서는 실행파일(sys.executable)이
있는 폴더를 기준으로 삼도록 분기합니다.
"""

import sys
from pathlib import Path

if getattr(sys, "frozen", False):
    # PyInstaller로 패키징되어 실행 중: .exe(또는 실행 바이너리)가 있는 폴더 기준
    BASE_DIR = Path(sys.executable).resolve().parent
else:
    # 개발 중 `python main.py`로 직접 실행: 이 파일이 있는 프로젝트 폴더 기준
    BASE_DIR = Path(__file__).resolve().parent

# 데이터베이스 파일 경로
DATABASE_DIR = BASE_DIR / "database"
DATABASE_PATH = DATABASE_DIR / "uga.db"
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

# 첨부파일 실제 저장 위치 (사용자가 업로드한 파일 복사본)
ATTACHMENTS_DIR = BASE_DIR / "assets" / "attachments"

# 내보내기(PDF/Markdown) 저장 위치
EXPORTS_DIR = BASE_DIR / "exports"

# 백업 저장 위치
BACKUPS_DIR = BASE_DIR / "backups"

# 앱 표시 이름
APP_NAME = "University Growth Archive"
APP_NAME_SHORT = "UGA"

# 필요한 폴더들을 앱 시작 시 자동으로 만들어 둡니다.
for directory in (DATABASE_DIR, ATTACHMENTS_DIR, EXPORTS_DIR, BACKUPS_DIR):
    directory.mkdir(parents=True, exist_ok=True)
