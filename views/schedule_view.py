"""
views/schedule_view.py

월별 달력 화면. 파이썬 표준 라이브러리 calendar 모듈로
'이번 달이 몇 주로 구성되는지, 1일이 무슨 요일인지'를 계산하고,
그 위에 Schedule 데이터를 얹어서 그립니다.
"""

import calendar
from datetime import date

import customtkinter as ctk
from tkinter import messagebox

from database.db_session import get_session
from services.schedule_service import ScheduleService
from utils.date_utils import days_until
from views.schedule_form_view import ScheduleFormView

TYPE_COLORS = {
    "박람회": "#F59E0B", "세미나": "#3B82F6", "시험": "#EF4444",
    "공모전": "#EF4444", "자격증": "#06B6D4", "기타": "#6B7280",
}

WEEKDAY_LABELS = ["월", "화", "수", "목", "금", "토", "일"]


class ScheduleView(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        today = date.today()
        self.current_year = today.year
        self.current_month = today.month

        self._build_ui()
        self.refresh()

    def _build_ui(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=24, pady=(20, 12))

        ctk.CTkButton(header, text="<", width=36, command=self._prev_month).pack(side="left")
        self.month_label = ctk.CTkLabel(
            header, text="", font=ctk.CTkFont(size=18, weight="bold")
        )
        self.month_label.pack(side="left", padx=12)
        ctk.CTkButton(header, text=">", width=36, command=self._next_month).pack(side="left")

        ctk.CTkButton(
            header, text="+ 새 일정 추가", width=130, command=self._handle_add_today
        ).pack(side="right")

        # 상단: 요일 헤더
        self.weekday_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.weekday_frame.pack(fill="x", padx=24)
        for i, label in enumerate(WEEKDAY_LABELS):
            self.weekday_frame.grid_columnconfigure(i, weight=1, uniform="wd")
            color = ("gray30", "gray70") if i < 5 else "#EF4444"
            ctk.CTkLabel(
                self.weekday_frame, text=label, font=ctk.CTkFont(size=12, weight="bold"),
                text_color=color,
            ).grid(row=0, column=i, sticky="ew", pady=4)

        # 달력 본문 (매번 다시 그림)
        self.calendar_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.calendar_frame.pack(fill="both", expand=True, padx=24, pady=(4, 20))

    def _prev_month(self):
        self.current_month -= 1
        if self.current_month == 0:
            self.current_month = 12
            self.current_year -= 1
        self.refresh()

    def _next_month(self):
        self.current_month += 1
        if self.current_month == 13:
            self.current_month = 1
            self.current_year += 1
        self.refresh()

    def refresh(self):
        self.month_label.configure(text=f"{self.current_year}년 {self.current_month}월")

        for widget in self.calendar_frame.winfo_children():
            widget.destroy()

        with get_session() as session:
            service = ScheduleService(session)
            schedules = service.get_month_schedules(self.current_year, self.current_month)
            grouped = service.group_by_day(schedules)

        cal = calendar.Calendar(firstweekday=0)  # 0 = 월요일 시작
        weeks = cal.monthdayscalendar(self.current_year, self.current_month)

        for col in range(7):
            self.calendar_frame.grid_columnconfigure(col, weight=1, uniform="day")
        for row in range(len(weeks)):
            self.calendar_frame.grid_rowconfigure(row, weight=1)

        today = date.today()
        for row, week in enumerate(weeks):
            for col, day in enumerate(week):
                if day == 0:
                    continue  # 이번 달에 속하지 않는 칸은 비워둠
                is_today = (
                    day == today.day and self.current_month == today.month
                    and self.current_year == today.year
                )
                cell = self._build_day_cell(day, grouped.get(day, []), is_today)
                cell.grid(row=row, column=col, sticky="nsew", padx=2, pady=2)

    def _build_day_cell(self, day: int, day_schedules: list, is_today: bool) -> ctk.CTkFrame:
        cell = ctk.CTkFrame(
            self.calendar_frame, corner_radius=8,
            fg_color=("#DBEAFE", "#1E3A5F") if is_today else ("gray92", "gray17"),
        )

        day_label = ctk.CTkLabel(
            cell, text=str(day), font=ctk.CTkFont(size=13, weight="bold" if is_today else "normal"),
            anchor="w",
        )
        day_label.pack(fill="x", padx=8, pady=(6, 2))
        day_label.bind("<Button-1>", lambda _e, d=day: self._handle_add_on_day(d))
        day_label.configure(cursor="hand2")

        for s in day_schedules[:3]:
            color = TYPE_COLORS.get(s.schedule_type.value, "#6B7280")
            chip = ctk.CTkLabel(
                cell, text=s.title, fg_color=color, text_color="white",
                corner_radius=6, font=ctk.CTkFont(size=10), anchor="w",
            )
            chip.pack(fill="x", padx=6, pady=1)
            chip.bind("<Button-1>", lambda _e, sid=s.id, st=s: self._handle_schedule_click(st))
            chip.configure(cursor="hand2")

        if len(day_schedules) > 3:
            ctk.CTkLabel(
                cell, text=f"+{len(day_schedules) - 3}개 더보기", font=ctk.CTkFont(size=10),
                text_color=("gray40", "gray60"), anchor="w",
            ).pack(fill="x", padx=6)

        return cell

    def _handle_add_today(self):
        ScheduleFormView(self, default_date=date.today(), on_saved=self.refresh)

    def _handle_add_on_day(self, day: int):
        picked = date(self.current_year, self.current_month, day)
        ScheduleFormView(self, default_date=picked, on_saved=self.refresh)

    def _handle_schedule_click(self, schedule):
        d = days_until(schedule.date)
        d_text = f"D-{d}" if d > 0 else ("D-Day" if d == 0 else f"{-d}일 지남")
        answer = messagebox.askyesno(
            schedule.title,
            f"날짜: {schedule.date}  ({d_text})\n종류: {schedule.schedule_type.value}\n"
            f"메모: {schedule.memo or '-'}\n\n이 일정을 삭제하시겠습니까?",
        )
        if answer:
            with get_session() as session:
                ScheduleService(session).delete_schedule(schedule.id)
            self.refresh()
