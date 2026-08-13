"""
views/activity_list_view.py

활동 전체 목록 화면. 검색창 + '새 활동 추가' 버튼 + 목록으로 구성됩니다.
"""

import customtkinter as ctk

from database.db_session import get_session
from services.activity_service import ActivityService
from views.components.card import ActivityRow


class ActivityListView(ctk.CTkFrame):
    def __init__(self, master, on_open_activity=None, on_add_activity=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.on_open_activity = on_open_activity
        self.on_add_activity = on_add_activity
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=24, pady=(20, 12))

        ctk.CTkLabel(
            header, text="전체 활동", font=ctk.CTkFont(size=20, weight="bold")
        ).pack(side="left")

        add_btn = ctk.CTkButton(
            header, text="+ 새 활동 추가", width=130, command=self._handle_add
        )
        add_btn.pack(side="right")

        self.search_entry = ctk.CTkEntry(
            self, placeholder_text="🔍 제목 / 장소 / 주최 / 내용으로 검색"
        )
        self.search_entry.pack(fill="x", padx=24, pady=(0, 12))
        self.search_entry.bind("<KeyRelease>", lambda _e: self.refresh())

        self.list_container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.list_container.pack(fill="both", expand=True, padx=24, pady=(0, 20))

    def refresh(self):
        keyword = self.search_entry.get().strip()

        for widget in self.list_container.winfo_children():
            widget.destroy()

        with get_session() as session:
            service = ActivityService(session)
            activities = service.search_activities(keyword) if keyword else service.list_activities()

            if not activities:
                ctk.CTkLabel(
                    self.list_container,
                    text="검색 결과가 없습니다." if keyword else "아직 기록된 활동이 없습니다. '+ 새 활동 추가'로 시작해보세요.",
                    text_color=("gray50", "gray60"),
                ).pack(pady=40)
                return

            for activity in activities:
                row = ActivityRow(self.list_container, activity, on_click=self._handle_open)
                row.pack(fill="x", pady=4)

    def _handle_open(self, activity_id: int):
        if self.on_open_activity:
            self.on_open_activity(activity_id)

    def _handle_add(self):
        if self.on_add_activity:
            self.on_add_activity()
