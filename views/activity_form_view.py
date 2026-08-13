"""
views/activity_form_view.py

활동을 추가하거나 수정할 때 뜨는 모달(별도 창)입니다.
CTkToplevel을 사용해 메인 창 위에 별도 창으로 띄웁니다.

activity가 None이면 '추가 모드', Activity 객체가 주어지면 '수정 모드'로 동작합니다.
"""

import customtkinter as ctk
from tkinter import messagebox

from database.db_session import get_session
from models.activity import ActivityType, ActivityStatus
from services.activity_service import ActivityService
from services.goal_service import GoalService
from services.category_service import CategoryService
from utils.date_utils import parse_date_short, format_date_short


class ActivityFormView(ctk.CTkToplevel):
    def __init__(self, master, activity=None, on_saved=None):
        super().__init__(master)
        self.activity = activity  # None이면 새 활동 추가
        self.on_saved = on_saved
        self.is_edit_mode = activity is not None

        self.title("활동 수정" if self.is_edit_mode else "새 활동 추가")
        self.geometry("500x820")
        self.resizable(False, False)
        self.grab_set()  # 모달로 만들기: 이 창이 닫힐 때까지 뒤 창 조작 불가

        self._build_ui()
        if self.is_edit_mode:
            self._load_activity_data()

    def _build_ui(self):
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=20, pady=20)

        self.title_entry = self._add_field(scroll, "제목 *")
        self.type_combo = self._add_combo(scroll, "활동 종류 *", [t.value for t in ActivityType])
        self.status_combo = self._add_combo(scroll, "상태", [s.value for s in ActivityStatus])
        self.date_entry = self._add_field(scroll, "시작일 * (YYYY-MM-DD)")
        self.location_entry = self._add_field(scroll, "장소")
        self.organizer_entry = self._add_field(scroll, "주최")

        ctk.CTkLabel(scroll, text="중요도 (1~5)", anchor="w").pack(fill="x", pady=(8, 2))
        self.importance_slider = ctk.CTkSlider(scroll, from_=1, to=5, number_of_steps=4)
        self.importance_slider.set(3)
        self.importance_slider.pack(fill="x", pady=(0, 8))

        self.purpose_entry = self._add_textbox(scroll, "참여 목적")
        self.content_entry = self._add_textbox(scroll, "활동 내용")
        self.tags_entry = self._add_field(scroll, "태그 (콤마로 구분, 예: AI, 반도체)")

        # 목표 연결 (V2): "없음" + 등록된 목표 목록 중에서 선택
        with get_session() as session:
            self._goal_choices = GoalService(session).list_goals()
        goal_labels = ["없음"] + [f"{g.title} ({g.period_label})" for g in self._goal_choices]
        self.goal_combo = self._add_combo(scroll, "연결할 목표 (선택)", goal_labels)

        # 자기소개서 분류 (V3): 체크박스 다중 선택
        with get_session() as session:
            self._category_choices = CategoryService(session).list_categories()
        ctk.CTkLabel(scroll, text="자기소개서 분류 (다중 선택 가능)", anchor="w").pack(
            fill="x", pady=(8, 4)
        )
        category_grid = ctk.CTkFrame(scroll, fg_color="transparent")
        category_grid.pack(fill="x", pady=(0, 8))
        self.category_vars: dict[int, ctk.BooleanVar] = {}
        for i, cat in enumerate(self._category_choices):
            var = ctk.BooleanVar(value=False)
            chk = ctk.CTkCheckBox(category_grid, text=cat.name, variable=var)
            chk.grid(row=i // 3, column=i % 3, sticky="w", padx=(0, 10), pady=3)
            self.category_vars[cat.id] = var

        # STAR (V4): 접었다 펼 수 있는 선택 섹션
        ctk.CTkLabel(
            scroll, text="STAR (선택 — 자기소개서/면접 답변용)", anchor="w",
            font=ctk.CTkFont(weight="bold"),
        ).pack(fill="x", pady=(14, 4))
        if self.is_edit_mode:
            ctk.CTkButton(
                scroll, text="🤖 AI로 STAR 초안 채우기", width=170, height=26,
                fg_color="transparent", border_width=1,
                command=self._handle_ai_fill_star,
            ).pack(anchor="w", pady=(0, 6))
        self.star_situation_entry = self._add_textbox(scroll, "Situation (상황)")
        self.star_task_entry = self._add_textbox(scroll, "Task (과제/목표)")
        self.star_action_entry = self._add_textbox(scroll, "Action (행동)")
        self.star_result_entry = self._add_textbox(scroll, "Result (결과)")

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

    def _load_activity_data(self):
        """수정 모드일 때 기존 데이터를 입력창에 채워넣습니다."""
        a = self.activity
        self.title_entry.insert(0, a.title)
        self.type_combo.set(a.activity_type.value)
        self.status_combo.set(a.status.value)
        self.date_entry.insert(0, format_date_short(a.date_start))
        if a.location:
            self.location_entry.insert(0, a.location)
        if a.organizer:
            self.organizer_entry.insert(0, a.organizer)
        self.importance_slider.set(a.importance)
        if a.purpose:
            self.purpose_entry.insert("1.0", a.purpose)
        if a.content:
            self.content_entry.insert("1.0", a.content)
        if a.tags:
            self.tags_entry.insert(0, ", ".join(t.name for t in a.tags))
        if a.goal_id:
            for g in self._goal_choices:
                if g.id == a.goal_id:
                    self.goal_combo.set(f"{g.title} ({g.period_label})")
                    break
        for cat in a.categories:
            if cat.id in self.category_vars:
                self.category_vars[cat.id].set(True)
        if a.star_situation:
            self.star_situation_entry.insert("1.0", a.star_situation)
        if a.star_task:
            self.star_task_entry.insert("1.0", a.star_task)
        if a.star_action:
            self.star_action_entry.insert("1.0", a.star_action)
        if a.star_result:
            self.star_result_entry.insert("1.0", a.star_result)

    def _handle_ai_fill_star(self):
        from services.ai_content_service import AIContentService
        from ai.ai_client import AIConfigError, AIRequestError

        with get_session() as session:
            try:
                draft = AIContentService(session).generate_star(self.activity)
            except AIConfigError as e:
                messagebox.showwarning("설정 필요", str(e), parent=self)
                return
            except AIRequestError as e:
                messagebox.showerror("생성 실패", str(e), parent=self)
                return
            except ValueError as e:
                messagebox.showwarning("생성 불가", str(e), parent=self)
                return

        self.star_situation_entry.delete("1.0", "end")
        self.star_situation_entry.insert("1.0", draft["situation"])
        self.star_task_entry.delete("1.0", "end")
        self.star_task_entry.insert("1.0", draft["task"])
        self.star_action_entry.delete("1.0", "end")
        self.star_action_entry.insert("1.0", draft["action"])
        self.star_result_entry.delete("1.0", "end")
        self.star_result_entry.insert("1.0", draft["result"])

    def _handle_save(self):
        title = self.title_entry.get().strip()
        if not title:
            messagebox.showwarning("입력 오류", "제목을 입력해주세요.", parent=self)
            return

        try:
            date_start = parse_date_short(self.date_entry.get())
        except ValueError:
            messagebox.showwarning(
                "입력 오류", "시작일은 YYYY-MM-DD 형식으로 입력해주세요. (예: 2026-03-15)", parent=self
            )
            return

        tag_names = [t.strip() for t in self.tags_entry.get().split(",") if t.strip()]
        category_names = [
            cat.name for cat in self._category_choices if self.category_vars[cat.id].get()
        ]

        goal_selection = self.goal_combo.get()
        goal_id = None
        if goal_selection != "없음":
            for g in self._goal_choices:
                if f"{g.title} ({g.period_label})" == goal_selection:
                    goal_id = g.id
                    break

        fields = dict(
            goal_id=goal_id,
            title=title,
            activity_type=ActivityType(self.type_combo.get()),
            status=ActivityStatus(self.status_combo.get()),
            date_start=date_start,
            location=self.location_entry.get().strip() or None,
            organizer=self.organizer_entry.get().strip() or None,
            importance=int(self.importance_slider.get()),
            purpose=self.purpose_entry.get("1.0", "end").strip() or None,
            content=self.content_entry.get("1.0", "end").strip() or None,
            tag_names=tag_names,
            category_names=category_names,
            star_situation=self.star_situation_entry.get("1.0", "end").strip() or None,
            star_task=self.star_task_entry.get("1.0", "end").strip() or None,
            star_action=self.star_action_entry.get("1.0", "end").strip() or None,
            star_result=self.star_result_entry.get("1.0", "end").strip() or None,
        )

        try:
            with get_session() as session:
                service = ActivityService(session)
                if self.is_edit_mode:
                    service.update_activity(self.activity.id, **fields)
                else:
                    service.create_activity(**fields)
        except ValueError as e:
            messagebox.showwarning("저장 실패", str(e), parent=self)
            return

        if self.on_saved:
            self.on_saved()
        self.destroy()
