# University Growth Archive (UGA) — V2

대학생활 4년을 기록하고 성장 흐름을 연결하는 "대학생 성장 운영체제".

## 실행 방법

```bash
pip install -r requirements.txt
python main.py
```

## 구현 범위

### V1
- 활동(Activity) CRUD (추가/조회/수정/삭제)
- 대시보드 (전체/완료/예정 통계, 다가오는 일정, 최근 활동)
- 태그 검색
- Reflection(회고) 기록
- 다크모드 / 라이트모드

### V2 (이번 업데이트)
- **목표(Goal) 관리**: 연간/학기/월간/주간 목표 생성, 진행률 바
  - 목표 활동 수(target_count)를 설정하면, 연결된 완료 활동 수 기준으로
    진행률이 **자동 계산**됩니다. (설정 안 하면 수동 입력값 사용)
  - 활동 추가/수정 시 "이 활동이 어떤 목표를 위한 것인지" 연결 가능
- **일정(Schedule) + 달력**: 월별 달력 뷰, 날짜 클릭으로 일정 추가,
  종류별 색상 구분 (박람회/세미나/시험/공모전/자격증/기타)
- **첨부파일 실제 업로드**: 활동 상세 화면에서 파일을 선택하면
  `assets/attachments/<activity_id>/` 아래로 실제 복사되고, "열기" 버튼으로
  OS 기본 프로그램으로 열람 가능

## 구조

전체 설계(아키텍처/DB/UI 와이어프레임/로드맵)는 `UGA_설계문서_V1.md`를 참고하세요.

```
uga/
├── main.py                # 진입점
├── config.py                # 경로/설정
├── models/                   # SQLAlchemy 테이블 정의
│   ├── activity.py            # 핵심 테이블 (goal_id로 Goal과 연결)
│   ├── goal.py                 # 목표
│   ├── schedule.py             # 일정
│   ├── attachment.py           # 첨부파일
│   ├── reflection.py           # 회고
│   └── tag.py                  # 태그 (N:M)
├── database/                 # 엔진/세션
├── repositories/               # DB CRUD 전담
├── services/                    # 비즈니스 로직 (진행률 계산, 파일 업로드 흐름 등)
├── views/                        # CustomTkinter 화면
│   ├── goal_view.py / goal_form_view.py
│   ├── schedule_view.py / schedule_form_view.py   # 달력
│   └── components/                                  # 재사용 위젯
└── utils/
    ├── date_utils.py
    └── file_utils.py            # 첨부파일 복사/열기
```

## 다음 버전 (V3)

- Category(자기소개서 분류) + Activity-Category 매핑 UI
- Matplotlib 기반 통계 뷰 (연도별/월별/분야별)
- PDF / Markdown export 기능
