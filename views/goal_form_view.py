"""
views/goal_form_view.py

목표 추가/수정 모달. activity_form_view.py와 구조가 거의 동일합니다
(같은 패턴을 재사용하면 나중에 유지보수할 때 어디서 뭘 고쳐야 할지 예측하기 쉬워집니다).
"""

import customtkinter as ctk
from tkinter import messagebox

from database.db_session import get_session
from models.goal import PeriodType
from services.goal_service import GoalService


class GoalFormView(ctk.CTkToplevel):
    def __init__(self, master, goal=None, on_saved=None):
        super().__init__(master)
        self.goal = goal
        self.on_saved = on_saved
        self.is_edit_mode = goal is not None

        self.title("목표 수정" if self.is_edit_mode else "새 목표 추가")
        self.geometry("420x480")
        self.resizable(False, False)
        self.grab_set()

        self._build_ui()
        if self.is_edit_mode:
            self._load_goal_data()

    def _build_ui(self):
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        self.title_entry = self._add_field(frame, "목표 제목 * (예: 공모전 3개 참가하기)")
        self.period_type_combo = self._add_combo(frame, "기간 종류", [p.value for p in PeriodType])
        self.period_label_entry = self._add_field(frame, "기간 라벨 * (예: 2026-1학기)")
        self.target_count_entry = self._add_field(frame, "목표 활동 수 (선택, 숫자만 - 자동 진행률 계산용)")
        self.description_box = self._add_textbox(frame, "목표 설명")

        ctk.CTkLabel(
            frame, text="※ 목표 활동 수를 입력하면, 이 목표에 연결된 완료된 활동 수로\n진행률이 자동 계산됩니다. 비워두면 활동 상세에서 목표를 선택해\n연결하세요.",
            font=ctk.CTkFont(size=11), text_color=("gray45", "gray65"), justify="left", anchor="w",
        ).pack(fill="x", pady=(4, 12))

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=(0, 16))
        ctk.CTkButton(btn_frame, text="취소", fg_color="gray40", command=self.destroy).pack(
            side="left", expand=True, fill="x", padx=(0, 6)
        )
        ctk.CTkButton(btn_frame, text="저장", command=self._handle_save).pack(
            side="left", expand=True, fill="x", padx=(6, 0)
        )

    def _add_field(self, parent, label: str) -> ctk.CTkEntry:
        ctk.CTkLabel(parent, text=label, anchor="w").pack(fill="x", pady=(8, 2))
        entry = ctk.CTkEntry(parent)
        entry.pack(fill="x")
        return entry

    def _add_combo(self, parent, label: str, values: list[str]) -> ctk.CTkComboBox:
        ctk.CTkLabel(parent, text=label, anchor="w").pack(fill="x", pady=(8, 2))
        combo = ctk.CTkComboBox(parent, values=values)
        combo.set(values[0])
        combo.pack(fill="x")
        return combo

    def _add_textbox(self, parent, label: str) -> ctk.CTkTextbox:
        ctk.CTkLabel(parent, text=label, anchor="w").pack(fill="x", pady=(8, 2))
        box = ctk.CTkTextbox(parent, height=70)
        box.pack(fill="x")
        return box

    def _load_goal_data(self):
        g = self.goal
        self.title_entry.insert(0, g.title)
        self.period_type_combo.set(g.period_type.value)
        self.period_label_entry.insert(0, g.period_label)
        if g.target_count:
            self.target_count_entry.insert(0, str(g.target_count))
        if g.target_description:
            self.description_box.insert("1.0", g.target_description)

    def _handle_save(self):
        title = self.title_entry.get().strip()
        period_label = self.period_label_entry.get().strip()

        if not title:
            messagebox.showwarning("입력 오류", "목표 제목을 입력해주세요.", parent=self)
            return
        if not period_label:
            messagebox.showwarning("입력 오류", "기간 라벨을 입력해주세요. (예: 2026-1학기)", parent=self)
            return

        target_count_raw = self.target_count_entry.get().strip()
        target_count = None
        if target_count_raw:
            if not target_count_raw.isdigit():
                messagebox.showwarning("입력 오류", "목표 활동 수는 숫자만 입력해주세요.", parent=self)
                return
            target_count = int(target_count_raw)

        fields = dict(
            title=title,
            period_type=PeriodType(self.period_type_combo.get()),
            period_label=period_label,
            target_description=self.description_box.get("1.0", "end").strip() or None,
            target_count=target_count,
        )

        try:
            with get_session() as session:
                service = GoalService(session)
                if self.is_edit_mode:
                    service.update_goal(self.goal.id, **fields)
                else:
                    service.create_goal(**fields)
        except ValueError as e:
            messagebox.showwarning("저장 실패", str(e), parent=self)
            return

        if self.on_saved:
            self.on_saved()
        self.destroy()
