"""
views/main_window.py

앱의 메인 윈도우입니다. 사이드바 + 현재 화면(content area)으로 구성되고,
"어떤 화면을 보여줄지" 를 관리하는 역할을 합니다.

화면 전환 방식: 매번 새로운 View 프레임을 만들어 content_frame 안에 pack하고,
이전 화면은 제거합니다. (여러 프레임을 미리 만들어두고 숨기는 방식도 있지만,
V1에서는 상세 화면이 activity_id에 따라 매번 새로 그려져야 하므로
'필요할 때 새로 만드는' 방식이 더 단순합니다.)
"""

import customtkinter as ctk

from config import APP_NAME
from database.db_session import init_db
from views.sidebar import Sidebar
from views.dashboard_view import DashboardView
from views.activity_list_view import ActivityListView
from views.activity_detail_view import ActivityDetailView
from views.activity_form_view import ActivityFormView
from views.goal_view import GoalView
from views.schedule_view import ScheduleView
from views.stats_view import StatsView
from views.cover_letter_view import CoverLetterView


class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        init_db()  # 최초 실행 시 테이블이 없으면 생성

        self.title(APP_NAME)
        self.geometry("1200x760")
        self.minsize(960, 640)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar = Sidebar(
            self, on_navigate=self.navigate, on_toggle_theme=self._toggle_theme
        )
        self.sidebar.grid(row=0, column=0, sticky="nsw")

        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.grid(row=0, column=1, sticky="nsew")

        self.current_view = None
        self.navigate("dashboard")
        self.sidebar.set_active("dashboard")

    # ---------- 화면 전환 ----------

    def navigate(self, screen: str):
        self._clear_content()

        if screen == "dashboard":
            self.current_view = DashboardView(
                self.content_frame, on_open_activity=self.open_activity_detail
            )
        elif screen == "activities":
            self.current_view = ActivityListView(
                self.content_frame,
                on_open_activity=self.open_activity_detail,
                on_add_activity=self.open_activity_form,
            )
        elif screen == "goals":
            self.current_view = GoalView(self.content_frame)
        elif screen == "schedule":
            self.current_view = ScheduleView(self.content_frame)
        elif screen == "stats":
            self.current_view = StatsView(self.content_frame)
        elif screen == "cover_letter":
            self.current_view = CoverLetterView(
                self.content_frame, on_open_activity=self.open_activity_detail
            )
        else:
            return

        self.current_view.pack(fill="both", expand=True)

    def open_activity_detail(self, activity_id: int):
        self._clear_content()
        self.current_view = ActivityDetailView(
            self.content_frame,
            activity_id=activity_id,
            on_back=lambda: self.navigate("activities"),
            on_deleted=lambda: self.navigate("activities"),
            on_edit=self._open_edit_form,
        )
        self.current_view.pack(fill="both", expand=True)

    def open_activity_form(self):
        """새 활동 추가 모달을 띄웁니다."""
        ActivityFormView(self, activity=None, on_saved=self._handle_activity_saved)

    def _open_edit_form(self, activity_id: int):
        from database.db_session import get_session
        from services.activity_service import ActivityService

        with get_session() as session:
            activity = ActivityService(session).get_activity(activity_id)
            # 모달이 닫힌 뒤 세션 밖에서도 값을 읽어야 하므로,
            # 필요한 속성들을 세션이 살아있는 지금 미리 로딩해둡니다.
            _ = (activity.title, activity.tags)  # lazy-load 강제 트리거
            ActivityFormView(
                self, activity=activity,
                on_saved=lambda: self._handle_activity_saved(reopen_id=activity_id),
            )

    def _handle_activity_saved(self, reopen_id: int | None = None):
        """활동 추가/수정 모달이 저장되고 닫혔을 때 호출됩니다."""
        if reopen_id:
            self.open_activity_detail(reopen_id)
        else:
            self.navigate("activities")

    # ---------- 테마 ----------

    def _toggle_theme(self, mode: str):
        ctk.set_appearance_mode(mode)

    # ---------- 내부 헬퍼 ----------

    def _clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
