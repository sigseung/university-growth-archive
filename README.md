# University Growth Archive (UGA) — V5

대학생활 4년을 기록하고, AI로 성장 관리·자기소개서·면접·커리어 관리까지
연결하는 "대학생 성장 운영체제". 로드맵의 V1~V5, 즉 설계 문서의 전체 기능이 담겼습니다.

## 실행 방법

```bash
pip install -r requirements.txt
python main.py
```

### 한글 폰트 (통계 그래프 / PDF export)
Windows/macOS는 기본 내장 폰트를 자동으로 찾아 씁니다. Linux는 나눔고딕이 필요합니다:
```bash
sudo apt-get install fonts-nanum
```

### AI 기능 사용 준비 (V5)
AI 기능(성장 분석 / 면접 준비 / 자소서 문장 생성 / Reflection·STAR 초안)을 쓰려면
OpenAI API 키가 필요합니다. 앱 실행 후 사이드바의 **설정** 화면에서 입력하면 됩니다.
(키는 `settings.json`에 로컬 저장되고, `.gitignore`에 등록되어 있어 GitHub에 올라가지 않습니다.)

터미널에서 매번 입력하지 않고 환경변수로 설정할 수도 있습니다:
```bash
export OPENAI_API_KEY=sk-...
```

## 구현 범위

### V1 — 활동 CRUD, 대시보드, 태그 검색, Reflection, 다크모드
### V2 — 목표(Goal) + 진행률 자동 계산, 일정(Schedule) + 달력, 첨부파일 업로드
### V3 — 자기소개서 분류(Category), 통계(Matplotlib), PDF/Markdown Export
### V4 — 성장 연결(GrowthLink), 커리어 타임라인, STAR 필드

### V5 (이번 업데이트) — AI 기능 통합
- **Reflection / STAR 초안 생성**: 활동 정보를 바탕으로 AI가 초안을 만들어 폼에 채워줌
  (저장은 사용자가 직접 확인 후 버튼을 눌러야 함 — AI가 임의로 DB를 바꾸지 않음)
- **자기소개서 문단 생성**: 카테고리(예: '협업')로 분류된 활동들을 모아 AI가 문단 초안 작성
- **면접 준비**: 활동 하나를 근거로 예상 질문 3개 + 꼬리질문 + 모범답변 생성,
  사용자가 직접 답변을 써보고 저장 가능
- **AI 성장 분석**: 전체 활동 통계를 근거로 성장 패턴 분석 + 다음 행동 추천,
  이력으로 저장되어 대시보드에도 최신 분석이 표시됨
- **설정 화면**: OpenAI API 키를 안전하게 로컬에 저장

AI 응답은 항상 정해진 JSON 형식으로 오도록 프롬프트에서 강제하고, 형식이 어긋나거나
API 키가 없거나 네트워크 오류가 나도 앱 전체가 죽지 않고 친절한 안내 메시지만
보여주도록 설계했습니다 (`ai/ai_client.py`의 `AIConfigError` / `AIRequestError`).

## 구조

전체 설계(아키텍처/DB/UI 와이어프레임/로드맵)는 `UGA_설계문서_V1.md`를 참고하세요.

```
uga/
├── main.py / config.py
├── models/
│   ├── activity.py            # STAR, GrowthLink, interview_qas 관계 모두 포함
│   ├── interview_qa.py           # 면접 준비 (V5)
│   ├── ai_analysis_log.py          # AI 분석 이력 (V5)
│   └── ... (growth_link, category, goal, schedule, attachment, reflection, tag)
├── ai/                                # V5: AI 기능 전담 레이어
│   ├── ai_client.py                     # OpenAI API 호출 (유일한 openai import 지점)
│   └── prompts/                           # 프롬프트 템플릿 (reflection/star/cover_letter/interview/growth_analysis)
├── database/ / repositories/ / services/
│   ├── ai_content_service.py                # Reflection/STAR/자소서/면접 생성
│   └── ai_analysis_service.py                 # 성장 분석 리포트 생성+저장
├── analytics/ / timeline/
├── views/
│   ├── interview_view.py                        # 면접 준비 화면 (V5)
│   ├── ai_analysis_view.py                         # AI 성장 분석 화면 (V5)
│   ├── settings_view.py                              # API 키 설정 화면 (V5)
│   └── ... (dashboard, activity_*, goal_*, schedule_*, stats, cover_letter, timeline)
└── utils/
    └── settings_store.py                                # API 키 로컬 저장 (V5)
```

## 다음 버전 (V6) — 완성도

- 자동 백업/복원
- PyInstaller로 .exe/.app 패키징
- 코드 리팩터링 + 테스트 코드 보강
- README + 스크린샷 정리 (GitHub 포트폴리오 마무리)
