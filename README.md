# University Growth Archive (UGA) — V1

대학생활 4년을 기록하고 성장 흐름을 연결하는 "대학생 성장 운영체제".

## 실행 방법

```bash
pip install -r requirements.txt
python main.py
```

## V1 범위

- 활동(Activity) CRUD (추가/조회/수정/삭제)
- 대시보드 (전체/완료/예정 통계, 다가오는 일정, 최근 활동)
- 태그 검색
- Reflection(회고) 기록
- 다크모드 / 라이트모드

## 구조

architecture, DB, 로드맵 등 전체 설계는 `UGA_설계문서_V1.md`를 참고하세요.

```
uga/
├── main.py            # 진입점
├── config.py           # 경로/설정
├── models/              # SQLAlchemy 테이블 정의
├── database/            # 엔진/세션
├── repositories/         # DB CRUD 전담
├── services/             # 비즈니스 로직
├── views/                # CustomTkinter 화면
│   └── components/        # 재사용 위젯
└── utils/                # 날짜 등 헬퍼
```

## 다음 버전 (V2)

- Goal(목표) 진행률 관리
- Schedule + 달력 뷰
- Attachment 실제 파일 업로드
