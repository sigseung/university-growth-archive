# University Growth Archive (UGA) — V3

대학생활 4년을 기록하고 성장 흐름을 연결하는 "대학생 성장 운영체제".

## 실행 방법

```bash
pip install -r requirements.txt
python main.py
```

### 참고: 한글 폰트 (통계 그래프 / PDF export)
통계 그래프와 PDF 내보내기에 한글이 필요합니다. Windows/macOS는 기본 내장 폰트
(맑은 고딕 / 애플 고딕)를 자동으로 찾아 쓰고, Linux는 나눔고딕이 필요합니다.
Ubuntu/Debian 계열이라면:
```bash
sudo apt-get install fonts-nanum
```
(폰트를 하나도 못 찾으면 그래프/PDF의 한글이 깨질 수 있습니다 — `utils/font_utils.py` 참고)

## 구현 범위

### V1
- 활동(Activity) CRUD, 대시보드, 태그 검색, Reflection, 다크모드

### V2
- 목표(Goal) 관리 + 진행률 자동 계산
- 일정(Schedule) + 달력
- 첨부파일 실제 업로드

### V3 (이번 업데이트)
- **자기소개서 분류(Category)**: 협업/문제해결/도전/창의성/리더십/책임감/성장/실패경험/성과
  9종 기본 제공. 활동 추가/수정 시 체크박스로 다중 선택.
- **자기소개서 관리 화면**: 카테고리 클릭 → 해당 경험만 필터링해서 조회
- **통계 화면**: Matplotlib 기반 4개 그래프
  - 연도별 활동 수 (막대)
  - 월별 활동 수 (막대)
  - 활동 종류별 비율 (파이)
  - 누적 성장 추이 (라인)
- **PDF / Markdown Export**: 활동 상세 화면에서 바로 내보내기
  (reportlab으로 한글 PDF 생성 — `.ttc` 폰트 컬렉션은 글리프가 깨지는 이슈가 있어
   반드시 단일 `.ttf` 파일만 사용하도록 처리했습니다)

## 구조

전체 설계(아키텍처/DB/UI 와이어프레임/로드맵)는 `UGA_설계문서_V1.md`를 참고하세요.

```
uga/
├── main.py / config.py
├── models/
│   ├── activity.py         # 핵심 테이블 (goal_id, categories 연결)
│   ├── category.py           # 자기소개서 분류 (V3)
│   ├── goal.py / schedule.py / attachment.py / reflection.py / tag.py
├── database/                 # 엔진/세션 (init_db 시 기본 카테고리 자동 시드)
├── repositories/               # DB CRUD 전담
├── services/
│   ├── activity_service.py     # 태그/카테고리 배정, 대시보드 통계
│   ├── category_service.py       # 카테고리 시드/조회 (V3)
│   ├── export_service.py          # PDF/Markdown export (V3)
│   ├── goal_service.py / schedule_service.py / attachment_service.py
├── analytics/                    # V3: 통계 집계 + Matplotlib 차트
│   ├── stats_calculator.py
│   └── chart_builder.py
├── views/
│   ├── stats_view.py               # 통계 화면 (V3)
│   ├── cover_letter_view.py          # 자소서 관리 화면 (V3)
│   ├── activity_detail_view.py, activity_form_view.py, ...
│   └── components/
└── utils/
    ├── date_utils.py / file_utils.py
    └── font_utils.py                 # 한글 폰트 탐색 (V3, .ttc 예외처리 포함)
```

## 다음 버전 (V4)

- 성장 연결 시스템 (GrowthLink): 활동 간 "이 경험으로 시작한 다음 행동" 연결
- 커리어 타임라인 시각화
- STAR 필드 (활동 모델 확장)
