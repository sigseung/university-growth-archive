# University Growth Archive (UGA) — V4

대학생활 4년을 기록하고 성장 흐름을 연결하는 "대학생 성장 운영체제".

## 실행 방법

```bash
pip install -r requirements.txt
python main.py
```

### 참고: 한글 폰트 (통계 그래프 / PDF export)
Windows/macOS는 기본 내장 폰트(맑은 고딕 / 애플 고딕)를 자동으로 찾아 씁니다.
Linux는 나눔고딕이 필요합니다:
```bash
sudo apt-get install fonts-nanum
```

## 구현 범위

### V1 — 활동 CRUD, 대시보드, 태그 검색, Reflection, 다크모드
### V2 — 목표(Goal) + 진행률 자동 계산, 일정(Schedule) + 달력, 첨부파일 업로드
### V3 — 자기소개서 분류(Category), 통계(Matplotlib), PDF/Markdown Export

### V4 (이번 업데이트) — 이 프로젝트의 정체성
- **성장 연결(GrowthLink)**: 활동 A가 활동 B로 이어졌다는 인과관계를 저장.
  활동 상세 화면에서 "연결된 다음 행동"을 추가/해제할 수 있고,
  연결 이유(link_reason)도 함께 기록됩니다.
- **커리어 타임라인**: 활동을 연도별로 묶어 세로로 나열하고, GrowthLink로
  연결된 활동은 `↳ 다음 행동: ...` 형태로 표시. 활동 종류별 색상 구분 +
  종류별 필터 버튼.
- **STAR 필드**: Situation/Task/Action/Result를 활동에 기록. 자기소개서/면접
  준비의 기본 골격이며, PDF/Markdown export에도 자동 포함됩니다.

## 구조

전체 설계(아키텍처/DB/UI 와이어프레임/로드맵)는 `UGA_설계문서_V1.md`를 참고하세요.

```
uga/
├── main.py / config.py
├── models/
│   ├── activity.py          # STAR 필드, outgoing/incoming_links 관계 추가 (V4)
│   ├── growth_link.py         # 성장 연결 (V4, 자기참조 N:M)
│   ├── category.py / goal.py / schedule.py / attachment.py / reflection.py / tag.py
├── database/                    # 엔진/세션 (init_db 시 기본 카테고리 자동 시드)
├── repositories/
│   └── growth_link_repository.py  # V4
├── services/
│   └── growth_link_service.py       # V4: 연결 생성/해제, 자기참조 방지 검증
├── analytics/                        # 통계 집계 + Matplotlib 차트
├── timeline/                           # V4: 타임라인 데이터 가공
│   └── timeline_builder.py
├── views/
│   ├── timeline_view.py                # 커리어 타임라인 (V4)
│   ├── activity_detail_view.py           # STAR + 성장 연결 섹션 추가 (V4)
│   ├── activity_form_view.py               # STAR 입력 섹션 추가 (V4)
│   └── ... (stats_view, cover_letter_view, goal_view, schedule_view, ...)
└── utils/
```

## 다음 버전 (V5) — AI 기능 통합

- OpenAI API 연동
- Reflection/STAR 자동 생성, 자기소개서 문장 생성, 면접 예상질문/모범답변
- AI 성장 분석 리포트
