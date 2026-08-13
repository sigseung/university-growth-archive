"""
views/timeline_view.py

커리어 타임라인 화면. 연도별로 활동을 세로로 나열하고,
GrowthLink로 연결된 활동은 "↳ 다음 행동" 형태로 들여써서 보여줍니다.

설계 문서의 예시:
    2026
    ├── AI Summit Seoul 참가
            ↓
    2027
    ├── Python 프로젝트

CustomTkinter에는 임의의 곡선/화살표를 쉽게 그릴 방법이 마땅치 않아서,
"화살표를 실제로 그리는" 대신 "↳ 다음 행동:" 텍스트로 인과관계를 표현했습니다.
(구현 복잡도 대비 가독성이 더 좋다고 판단 — 나중에 원한다면 Canvas로
실제 연결선을 그리는 것도 가능하지만, 지금은 데이터가 정확히 보이는 게 우선)
"""

import customtkinter as ctk

from database.db_session import get_session
from services.activity_service import ActivityService
from timeline.timeline_builder import group_by_year, type_color
from utils.date_utils import format_date_kr
from models.activity import ActivityType


class TimelineView(ctk.CTkFrame):
    def __init__(self, master, on_open_activity=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.on_open_activity = on_open_activity
        self.active_filter: str | None = None  # None = 전체
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        ctk.CTkLabel(
            self, text="커리어 타임라인", font=ctk.CTkFont(size=20, weight="bold"), anchor="w"
        ).pack(fill="x", padx=24, pady=(20, 12))

        self.filter_bar = ctk.CTkFrame(self, fg_color="transparent")
        self.filter_bar.pack(fill="x", padx=24, pady=(0, 12))

        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True, padx=24, pady=(0, 20))

    def refresh(self):
        self._render_filter_bar()
        self._render_timeline()

    def _render_filter_bar(self):
        for widget in self.filter_bar.winfo_children():
            widget.destroy()

        all_btn = ctk.CTkButton(
            self.filter_bar, text="전체", width=0, height=30,
            fg_color=("gray75", "gray30") if self.active_filter is None else "transparent",
            border_width=1, command=lambda: self._set_filter(None),
        )
        all_btn.pack(side="left", padx=(0, 6))

        for t in ActivityType:
            is_active = self.active_filter == t.value
            btn = ctk.CTkButton(
                self.filter_bar, text=t.value, width=0, height=30,
                fg_color=type_color(t.value) if is_active else "transparent",
                border_width=1, border_color=type_color(t.value),
                command=lambda v=t.value: self._set_filter(v),
            )
            btn.pack(side="left", padx=(0, 6))

    def _set_filter(self, type_value: str | None):
        self.active_filter = type_value
        self.refresh()

    def _render_timeline(self):
        for widget in self.scroll.winfo_children():
            widget.destroy()

        with get_session() as session:
            activities = ActivityService(session).list_activities()

            if self.active_filter:
                activities = [a for a in activities if a.activity_type.value == self.active_filter]

            if not activities:
                ctk.CTkLabel(
                    self.scroll, text="표시할 활동이 없습니다.", text_color=("gray50", "gray60")
                ).pack(pady=40)
                return

            by_year = group_by_year(activities)

            for year, year_activities in by_year.items():
                ctk.CTkLabel(
                    self.scroll, text=str(year), font=ctk.CTkFont(size=18, weight="bold"), anchor="w"
                ).pack(fill="x", pady=(16, 8))
                ctk.CTkFrame(self.scroll, height=2, fg_color=("gray80", "gray30")).pack(fill="x", pady=(0, 10))

                for activity in year_activities:
                    self._render_activity_row(activity)

    def _render_activity_row(self, activity):
        row = ctk.CTkFrame(self.scroll, fg_color="transparent")
        row.pack(fill="x", pady=3, anchor="w")

        dot_color = type_color(activity.activity_type.value)
        dot = ctk.CTkLabel(row, text="●", text_color=dot_color, font=ctk.CTkFont(size=16))
        dot.grid(row=0, column=0, padx=(4, 8), sticky="n")

        info_frame = ctk.CTkFrame(row, fg_color="transparent", cursor="hand2")
        info_frame.grid(row=0, column=1, sticky="w")

        title_label = ctk.CTkLabel(
            info_frame, text=f"{activity.title}", font=ctk.CTkFont(size=14, weight="bold"), anchor="w",
        )
        title_label.pack(anchor="w")
        meta_label = ctk.CTkLabel(
            info_frame,
            text=f"{activity.activity_type.value}  ·  {format_date_kr(activity.date_start)}",
            font=ctk.CTkFont(size=11), text_color=("gray40", "gray70"), anchor="w",
        )
        meta_label.pack(anchor="w")

        for widget in (info_frame, title_label, meta_label):
            widget.bind("<Button-1>", lambda _e, aid=activity.id: self._handle_open(aid))

        # 성장 연결(GrowthLink): "이 활동을 계기로 시작한 다음 행동"들을 들여써서 표시
        for link in activity.outgoing_links:
            link_label = ctk.CTkLabel(
                self.scroll,
                text=f"      ↳ 다음 행동: {link.to_activity.title}" + (
                    f"  ({link.link_reason})" if link.link_reason else ""
                ),
                font=ctk.CTkFont(size=12), text_color=("gray35", "gray65"), anchor="w", cursor="hand2",
            )
            link_label.pack(fill="x", pady=(0, 2), anchor="w")
            link_label.bind(
                "<Button-1>", lambda _e, aid=link.to_activity_id: self._handle_open(aid)
            )

    def _handle_open(self, activity_id: int):
        if self.on_open_activity:
            self.on_open_activity(activity_id)
