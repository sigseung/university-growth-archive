"""
views/activity_detail_view.py

활동 하나의 상세 정보를 보여주는 화면입니다.
V1에서는 기본정보 + Reflection 섹션까지만 구현합니다.
(STAR, 첨부파일, 연결된 다음 행동 탭은 V3~V4에서 이 파일에 탭을 추가하는 방식으로 확장)
"""

import customtkinter as ctk
from tkinter import messagebox

from database.db_session import get_session
from models.reflection import Reflection
from services.activity_service import ActivityService
from utils.date_utils import format_date_kr


class ActivityDetailView(ctk.CTkFrame):
    def __init__(self, master, activity_id: int, on_back=None, on_deleted=None, on_edit=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.activity_id = activity_id
        self.on_back = on_back
        self.on_deleted = on_deleted
        self.on_edit = on_edit
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        top_bar = ctk.CTkFrame(self, fg_color="transparent")
        top_bar.pack(fill="x", padx=24, pady=(20, 8))

        ctk.CTkButton(
            top_bar, text="< 목록으로", width=100, fg_color="transparent",
            border_width=1, command=lambda: self.on_back() if self.on_back else None,
        ).pack(side="left")

        self.edit_btn = ctk.CTkButton(top_bar, text="수정", width=70, command=self._handle_edit)
        self.edit_btn.pack(side="right", padx=(6, 0))
        self.delete_btn = ctk.CTkButton(
            top_bar, text="삭제", width=70, fg_color="#EF4444", hover_color="#DC2626",
            command=self._handle_delete,
        )
        self.delete_btn.pack(side="right")

        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True, padx=24, pady=(0, 20))

    def refresh(self):
        for widget in self.scroll.winfo_children():
            widget.destroy()

        with get_session() as session:
            service = ActivityService(session)
            activity = service.get_activity(self.activity_id)

            if activity is None:
                ctk.CTkLabel(self.scroll, text="활동을 찾을 수 없습니다.").pack(pady=40)
                return

            ctk.CTkLabel(
                self.scroll, text=activity.title, font=ctk.CTkFont(size=22, weight="bold"), anchor="w"
            ).pack(fill="x", pady=(4, 4))

            meta = (
                f"{activity.activity_type.value}  ·  {format_date_kr(activity.date_start)}  ·  "
                f"{activity.location or '장소 미정'}  ·  상태: {activity.status.value}  ·  "
                f"중요도: {'★' * activity.importance}{'☆' * (5 - activity.importance)}"
            )
            ctk.CTkLabel(
                self.scroll, text=meta, font=ctk.CTkFont(size=13),
                text_color=("gray40", "gray70"), anchor="w",
            ).pack(fill="x", pady=(0, 6))

            if activity.tags:
                tag_frame = ctk.CTkFrame(self.scroll, fg_color="transparent")
                tag_frame.pack(fill="x", pady=(0, 16), anchor="w")
                for tag in activity.tags:
                    ctk.CTkLabel(
                        tag_frame, text=f"#{tag.name}", fg_color=("gray85", "gray25"),
                        corner_radius=8, padx=8,
                    ).pack(side="left", padx=(0, 6))

            self._section(self.scroll, "참여 목적", activity.purpose)
            self._section(self.scroll, "활동 내용", activity.content)
            self._section(self.scroll, "새롭게 배운 기술", activity.new_skills)
            self._section(self.scroll, "새롭게 알게 된 직무", activity.new_roles)

            self._reflection_section(self.scroll, activity)

    def _section(self, parent, title: str, content: str | None):
        if not content:
            return
        ctk.CTkLabel(
            parent, text=title, font=ctk.CTkFont(size=14, weight="bold"), anchor="w"
        ).pack(fill="x", pady=(14, 4))
        ctk.CTkLabel(
            parent, text=content, anchor="w", justify="left", wraplength=700
        ).pack(fill="x")

    def _reflection_section(self, parent, activity):
        ctk.CTkLabel(
            parent, text="Reflection (회고)", font=ctk.CTkFont(size=14, weight="bold"), anchor="w"
        ).pack(fill="x", pady=(20, 8))

        if not activity.reflections:
            ctk.CTkLabel(
                parent, text="아직 작성한 회고가 없습니다.", text_color=("gray50", "gray60"), anchor="w"
            ).pack(fill="x", pady=(0, 8))
        else:
            for r in activity.reflections:
                box = ctk.CTkFrame(parent, corner_radius=10)
                box.pack(fill="x", pady=4)
                if r.learned:
                    ctk.CTkLabel(
                        box, text=f"느낀 점: {r.learned}", anchor="w", justify="left", wraplength=680
                    ).pack(fill="x", padx=12, pady=(10, 2))
                if r.next_action:
                    ctk.CTkLabel(
                        box, text=f"앞으로 할 행동: {r.next_action}", anchor="w",
                        justify="left", wraplength=680, text_color=("gray30", "gray80"),
                    ).pack(fill="x", padx=12, pady=(0, 10))

        add_frame = ctk.CTkFrame(parent, fg_color="transparent")
        add_frame.pack(fill="x", pady=(8, 0))

        self.learned_box = ctk.CTkTextbox(add_frame, height=50)
        self.learned_box.pack(fill="x")
        self.learned_box.configure(border_width=1)
        self.next_action_box = ctk.CTkTextbox(add_frame, height=50)
        self.next_action_box.pack(fill="x", pady=(6, 0))

        ctk.CTkButton(
            add_frame, text="+ 회고 추가", command=self._handle_add_reflection
        ).pack(anchor="e", pady=(8, 0))

    def _handle_add_reflection(self):
        learned = self.learned_box.get("1.0", "end").strip()
        next_action = self.next_action_box.get("1.0", "end").strip()
        if not learned and not next_action:
            return

        with get_session() as session:
            reflection = Reflection(
                activity_id=self.activity_id,
                learned=learned or None,
                next_action=next_action or None,
            )
            session.add(reflection)
            session.commit()

        self.refresh()

    def _handle_edit(self):
        if self.on_edit:
            self.on_edit(self.activity_id)

    def _handle_delete(self):
        if not messagebox.askyesno("삭제 확인", "이 활동을 삭제하시겠습니까? 되돌릴 수 없습니다."):
            return
        with get_session() as session:
            service = ActivityService(session)
            service.delete_activity(self.activity_id)
        if self.on_deleted:
            self.on_deleted()
