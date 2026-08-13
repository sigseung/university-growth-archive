"""
config.py

프로젝트 전체에서 공유하는 설정값을 모아두는 파일입니다.
'경로를 코드 여기저기에 하드코딩하지 않는다'는 원칙을 지키기 위한 곳입니다.
나중에 배포용 실행파일(.exe)을 만들 때도 이 파일 하나만 손보면 됩니다.
"""

from pathlib import Path

# 프로젝트 루트 디렉토리 (이 파일이 있는 위치 기준)
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
