"""
views/dashboard_view.py

홈 화면(대시보드). V1에서는 아래 4가지만 구현합니다.
    - 오늘 날짜
    - 통계 카드 (전체/완료/예정)
    - 다가오는 일정 (Activity 중 date_start가 미래인 것)
    - 최근 활동 목록

나머지(성장 그래프, AI 분석, 목표 진행률 등)는 각 기능이 실제로
구현되는 V3~V5 시점에 이 파일을 확장합니다. 지금 빈 자리표시자를
넣지 않는 이유: 동작하지 않는 UI를 미리 만들어두면 오히려
"이거 왜 안 눌리지?" 하는 혼란만 생기기 때문입니다.
"""

from datetime import date

import customtkinter as ctk

from database.db_session import get_session
from services.activity_service import ActivityService
from utils.date_utils import format_date_kr, days_until
from views.components.card import StatCard, ActivityRow


class DashboardView(ctk.CTkFrame):
    def __init__(self, master, on_open_activity=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.on_open_activity = on_open_activity
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        # 상단: 오늘 날짜
        self.date_label = ctk.CTkLabel(
            self, text="", font=ctk.CTkFont(size=15, weight="bold"), anchor="w"
        )
        self.date_label.pack(fill="x", padx=24, pady=(20, 12))

        # 통계 카드 3개 (가로 배치)
        self.stat_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.stat_frame.pack(fill="x", padx=24, pady=(0, 20))
        self.stat_frame.grid_columnconfigure((0, 1, 2), weight=1, uniform="stat")

        self.card_total = StatCard(self.stat_frame, "전체 활동", "0")
        self.card_total.grid(row=0, column=0, padx=(0, 8), sticky="ew")
        self.card_done = StatCard(self.stat_frame, "참여 완료", "0")
        self.card_done.grid(row=0, column=1, padx=8, sticky="ew")
        self.card_upcoming = StatCard(self.stat_frame, "참여 예정", "0")
        self.card_upcoming.grid(row=0, column=2, padx=(8, 0), sticky="ew")

        # 다가오는 일정 + 최근 활동 (좌우 배치)
        self.body_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.body_frame.pack(fill="both", expand=True, padx=24, pady=(0, 20))
        self.body_frame.grid_columnconfigure((0, 1), weight=1, uniform="body")
        self.body_frame.grid_rowconfigure(0, weight=1)

        self.upcoming_box = self._make_section(self.body_frame, "📅 다가오는 일정")
        self.upcoming_box.grid(row=0, column=0, padx=(0, 8), sticky="nsew")

        self.recent_box = self._make_section(self.body_frame, "🕒 최근 활동")
        self.recent_box.grid(row=0, column=1, padx=(8, 0), sticky="nsew")

    def _make_section(self, parent, title: str) -> ctk.CTkFrame:
        frame = ctk.CTkFrame(parent, corner_radius=12)
        header = ctk.CTkLabel(frame, text=title, font=ctk.CTkFont(size=14, weight="bold"))
        header.pack(anchor="w", padx=16, pady=(14, 8))
        content = ctk.CTkScrollableFrame(frame, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=8, pady=(0, 10))
        frame.content = content  # 나중에 내용 채울 때 접근하기 위한 참조 저장
        return frame

    def refresh(self):
        """DB에서 최신 데이터를 다시 읽어와 화면을 갱신합니다.
        다른 화면에서 활동을 추가/수정한 뒤 대시보드로 돌아올 때 호출됩니다."""
        self.date_label.configure(text=f"오늘: {format_date_kr(date.today())}")

        with get_session() as session:
            service = ActivityService(session)
            stats = service.get_dashboard_stats()
            self.card_total.set_value(str(stats["total"]))
            self.card_done.set_value(str(stats["done"]))
            self.card_upcoming.set_value(str(stats["upcoming"]))

            upcoming = service.get_upcoming_activities(limit=8)
            self._fill_activity_list(self.upcoming_box.content, upcoming, empty_text="예정된 일정이 없습니다.")

            recent = service.list_activities()[:8]
            self._fill_activity_list(self.recent_box.content, recent, empty_text="아직 기록된 활동이 없습니다.")

    def _fill_activity_list(self, container, activities, empty_text: str):
        for widget in container.winfo_children():
            widget.destroy()

        if not activities:
            ctk.CTkLabel(
                container, text=empty_text, text_color=("gray50", "gray60")
            ).pack(pady=20)
            return

        for activity in activities:
            row = ActivityRow(container, activity, on_click=self._open_activity)
            row.pack(fill="x", pady=4)

            if activity.date_start >= date.today():
                d = days_until(activity.date_start)
                d_text = "D-Day" if d == 0 else f"D-{d}"
                ctk.CTkLabel(
                    row, text=d_text, font=ctk.CTkFont(size=11, weight="bold"),
                    text_color=("gray30", "gray80"),
                ).grid(row=0, column=2, rowspan=2, padx=12)

    def _open_activity(self, activity_id: int):
        if self.on_open_activity:
            self.on_open_activity(activity_id)
