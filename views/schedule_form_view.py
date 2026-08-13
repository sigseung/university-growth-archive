"""
views/schedule_form_view.py

일정 추가 모달. 특정 날짜를 클릭한 상태로 열리면 그 날짜가 기본값으로 채워집니다.
"""

import customtkinter as ctk
from tkinter import messagebox
from datetime import date

from database.db_session import get_session
from models.schedule import ScheduleType
from services.schedule_service import ScheduleService
from utils.date_utils import parse_date_short, format_date_short


class ScheduleFormView(ctk.CTkToplevel):
    def __init__(self, master, default_date: date | None = None, on_saved=None):
        super().__init__(master)
        self.on_saved = on_saved

        self.title("새 일정 추가")
        self.geometry("380x360")
        self.resizable(False, False)
        self.grab_set()

        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(frame, text="일정 제목 *", anchor="w").pack(fill="x", pady=(0, 2))
        self.title_entry = ctk.CTkEntry(frame)
        self.title_entry.pack(fill="x")

        ctk.CTkLabel(frame, text="날짜 * (YYYY-MM-DD)", anchor="w").pack(fill="x", pady=(10, 2))
        self.date_entry = ctk.CTkEntry(frame)
        self.date_entry.insert(0, format_date_short(default_date or date.today()))
        self.date_entry.pack(fill="x")

        ctk.CTkLabel(frame, text="종류", anchor="w").pack(fill="x", pady=(10, 2))
        self.type_combo = ctk.CTkComboBox(frame, values=[t.value for t in ScheduleType])
        self.type_combo.set(ScheduleType.ETC.value)
        self.type_combo.pack(fill="x")

        ctk.CTkLabel(frame, text="메모", anchor="w").pack(fill="x", pady=(10, 2))
        self.memo_entry = ctk.CTkEntry(frame)
        self.memo_entry.pack(fill="x")

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=(0, 16))
        ctk.CTkButton(btn_frame, text="취소", fg_color="gray40", command=self.destroy).pack(
            side="left", expand=True, fill="x", padx=(0, 6)
        )
        ctk.CTkButton(btn_frame, text="저장", command=self._handle_save).pack(
            side="left", expand=True, fill="x", padx=(6, 0)
        )

    def _handle_save(self):
        title = self.title_entry.get().strip()
        if not title:
            messagebox.showwarning("입력 오류", "일정 제목을 입력해주세요.", parent=self)
            return

        try:
            schedule_date = parse_date_short(self.date_entry.get())
        except ValueError:
            messagebox.showwarning("입력 오류", "날짜는 YYYY-MM-DD 형식으로 입력해주세요.", parent=self)
            return

        with get_session() as session:
            ScheduleService(session).create_schedule(
                title=title,
                schedule_date=schedule_date,
                schedule_type=ScheduleType(self.type_combo.get()),
                memo=self.memo_entry.get().strip() or None,
            )

        if self.on_saved:
            self.on_saved()
        self.destroy()
