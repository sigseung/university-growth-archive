"""
views/goal_view.py

목표 목록 화면. 각 목표를 진행률 바(progress bar)가 있는 카드로 보여줍니다.
"""

import customtkinter as ctk
from tkinter import messagebox

from database.db_session import get_session
from services.goal_service import GoalService
from views.goal_form_view import GoalFormView


class GoalView(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=24, pady=(20, 12))

        ctk.CTkLabel(
            header, text="목표", font=ctk.CTkFont(size=20, weight="bold")
        ).pack(side="left")

        ctk.CTkButton(
            header, text="+ 새 목표 추가", width=130, command=self._handle_add
        ).pack(side="right")

        self.list_container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.list_container.pack(fill="both", expand=True, padx=24, pady=(0, 20))

    def refresh(self):
        for widget in self.list_container.winfo_children():
            widget.destroy()

        with get_session() as session:
            service = GoalService(session)
            goals = service.list_goals()

            if not goals:
                ctk.CTkLabel(
                    self.list_container,
                    text="아직 등록된 목표가 없습니다. '+ 새 목표 추가'로 시작해보세요.",
                    text_color=("gray50", "gray60"),
                ).pack(pady=40)
                return

            for goal in goals:
                self._render_goal_card(self.list_container, goal, service)

    def _render_goal_card(self, parent, goal, service: GoalService):
        card = ctk.CTkFrame(parent, corner_radius=12)
        card.pack(fill="x", pady=6)

        top_row = ctk.CTkFrame(card, fg_color="transparent")
        top_row.pack(fill="x", padx=16, pady=(14, 4))

        ctk.CTkLabel(
            top_row, text=goal.title, font=ctk.CTkFont(size=15, weight="bold"), anchor="w"
        ).pack(side="left")

        badge_text = f"{goal.period_type.value} · {goal.period_label}"
        ctk.CTkLabel(
            top_row, text=badge_text, font=ctk.CTkFont(size=11),
            text_color=("gray40", "gray70"),
        ).pack(side="left", padx=(10, 0))

        ctk.CTkButton(
            top_row, text="수정", width=50, height=24, fg_color="transparent",
            border_width=1, command=lambda: self._handle_edit(goal),
        ).pack(side="right", padx=(4, 0))
        ctk.CTkButton(
            top_row, text="삭제", width=50, height=24, fg_color="#EF4444", hover_color="#DC2626",
            command=lambda: self._handle_delete(goal.id),
        ).pack(side="right")

        if goal.target_description:
            ctk.CTkLabel(
                card, text=goal.target_description, anchor="w", justify="left",
                text_color=("gray30", "gray80"), wraplength=700,
            ).pack(fill="x", padx=16, pady=(0, 8))

        percent = service.calculate_progress(goal)
        progress_row = ctk.CTkFrame(card, fg_color="transparent")
        progress_row.pack(fill="x", padx=16, pady=(0, 14))

        bar = ctk.CTkProgressBar(progress_row)
        bar.set(percent / 100)
        bar.pack(side="left", fill="x", expand=True)

        label_text = f"{percent}%"
        if goal.target_count:
            done, total_linked = service.get_linked_activity_count(goal)
            label_text = f"{percent}%  ({done}/{goal.target_count} 완료)"

        ctk.CTkLabel(
            progress_row, text=label_text, font=ctk.CTkFont(size=12, weight="bold"), width=110,
        ).pack(side="left", padx=(10, 0))

    def _handle_add(self):
        GoalFormView(self, goal=None, on_saved=self.refresh)

    def _handle_edit(self, goal):
        GoalFormView(self, goal=goal, on_saved=self.refresh)

    def _handle_delete(self, goal_id: int):
        if not messagebox.askyesno("삭제 확인", "이 목표를 삭제하시겠습니까? 연결된 활동의 목표 연결도 해제됩니다."):
            return
        with get_session() as session:
            GoalService(session).delete_goal(goal_id)
        self.refresh()
