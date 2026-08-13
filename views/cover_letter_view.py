"""
views/cover_letter_view.py

자기소개서 관리 화면. 상단에 카테고리 버튼(협업/도전/리더십 등)이 있고,
하나를 클릭하면 그 카테고리로 분류된 활동만 아래에 필터링되어 보입니다.

설계 문서 원문: "협업을 클릭하면 협업 경험만 볼 수 있어야 한다."
→ 이 요구사항을 그대로 구현한 화면입니다.
"""

import customtkinter as ctk

from database.db_session import get_session
from services.category_service import CategoryService
from services.activity_service import ActivityService
from views.components.card import ActivityRow


class CoverLetterView(ctk.CTkFrame):
    def __init__(self, master, on_open_activity=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.on_open_activity = on_open_activity
        self.selected_category_id: int | None = None
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        ctk.CTkLabel(
            self, text="자기소개서 관리", font=ctk.CTkFont(size=20, weight="bold"), anchor="w"
        ).pack(fill="x", padx=24, pady=(20, 4))
        ctk.CTkLabel(
            self, text="카테고리를 클릭하면 해당 경험만 필터링해서 볼 수 있습니다.",
            font=ctk.CTkFont(size=12), text_color=("gray40", "gray70"), anchor="w",
        ).pack(fill="x", padx=24, pady=(0, 12))

        self.category_bar = ctk.CTkFrame(self, fg_color="transparent")
        self.category_bar.pack(fill="x", padx=24, pady=(0, 12))

        self.list_container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.list_container.pack(fill="both", expand=True, padx=24, pady=(0, 20))

    def refresh(self):
        for widget in self.category_bar.winfo_children():
            widget.destroy()

        with get_session() as session:
            categories = CategoryService(session).list_categories()
            counts = {c.id: len(c.activities) for c in categories}

            for cat in categories:
                is_selected = cat.id == self.selected_category_id
                btn = ctk.CTkButton(
                    self.category_bar, text=f"{cat.name} ({counts.get(cat.id, 0)})",
                    width=0, height=32,
                    fg_color=("gray75", "gray30") if is_selected else "transparent",
                    border_width=1,
                    command=lambda cid=cat.id: self._select_category(cid),
                )
                btn.pack(side="left", padx=(0, 6), pady=2)

            self._render_activity_list(session)

    def _render_activity_list(self, session):
        for widget in self.list_container.winfo_children():
            widget.destroy()

        if self.selected_category_id is None:
            ctk.CTkLabel(
                self.list_container,
                text="위에서 카테고리를 선택하면 해당 경험이 여기에 나타납니다.",
                text_color=("gray50", "gray60"),
            ).pack(pady=40)
            return

        activity_service = ActivityService(session)
        activities = activity_service.get_activities_by_category(self.selected_category_id)

        if not activities:
            ctk.CTkLabel(
                self.list_container, text="이 카테고리로 분류된 활동이 아직 없습니다.\n"
                "활동을 추가하거나 수정할 때 자기소개서 분류 체크박스를 선택해보세요.",
                text_color=("gray50", "gray60"), justify="left",
            ).pack(pady=40)
            return

        for activity in activities:
            row = ActivityRow(self.list_container, activity, on_click=self._handle_open)
            row.pack(fill="x", pady=4)

    def _select_category(self, category_id: int):
        # 같은 카테고리를 다시 누르면 선택 해제 (토글)
        self.selected_category_id = None if self.selected_category_id == category_id else category_id
        self.refresh()

    def _handle_open(self, activity_id: int):
        if self.on_open_activity:
            self.on_open_activity(activity_id)
