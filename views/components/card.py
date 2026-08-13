"""
views/components/card.py

대시보드 등 여러 화면에서 반복적으로 쓰이는 '카드' 위젯입니다.
같은 스타일의 카드를 매번 새로 만들지 않고 이 클래스를 재사용합니다.
"""

import customtkinter as ctk


class StatCard(ctk.CTkFrame):
    """숫자 하나를 강조해서 보여주는 카드. 예: '전체 활동 47'."""

    def __init__(self, master, label: str, value: str, **kwargs):
        super().__init__(master, corner_radius=12, **kwargs)

        self.value_label = ctk.CTkLabel(
            self, text=value, font=ctk.CTkFont(size=28, weight="bold")
        )
        self.value_label.pack(padx=16, pady=(16, 0), anchor="w")

        self.desc_label = ctk.CTkLabel(
            self, text=label, font=ctk.CTkFont(size=13), text_color=("gray40", "gray70")
        )
        self.desc_label.pack(padx=16, pady=(0, 16), anchor="w")

    def set_value(self, value: str):
        self.value_label.configure(text=value)


class ActivityRow(ctk.CTkFrame):
    """활동 목록의 한 줄(row)을 표현하는 카드.
    클릭하면 on_click 콜백이 activity_id와 함께 호출됩니다."""

    def __init__(self, master, activity, on_click=None, **kwargs):
        super().__init__(master, corner_radius=10, **kwargs)
        self.activity = activity
        self.on_click = on_click

        type_colors = {
            "박람회": "#F59E0B", "세미나": "#3B82F6", "프로젝트": "#10B981",
            "공모전": "#EF4444", "연구실": "#8B5CF6", "자격증": "#06B6D4",
            "대외활동": "#EC4899", "동아리": "#F97316", "봉사": "#84CC16",
            "독서": "#6366F1", "수업프로젝트": "#14B8A6", "운동": "#F43F5E",
            "기타": "#6B7280",
        }
        type_value = activity.activity_type.value if hasattr(activity.activity_type, "value") else str(activity.activity_type)
        color = type_colors.get(type_value, "#6B7280")

        badge = ctk.CTkLabel(
            self, text=type_value, fg_color=color, text_color="white",
            corner_radius=8, width=70, font=ctk.CTkFont(size=11, weight="bold"),
        )
        badge.grid(row=0, column=0, rowspan=2, padx=(12, 10), pady=12)

        title_label = ctk.CTkLabel(
            self, text=activity.title, font=ctk.CTkFont(size=15, weight="bold"), anchor="w"
        )
        title_label.grid(row=0, column=1, sticky="w", pady=(10, 0))

        meta_text = f"{activity.date_start}  ·  {activity.location or '장소 미정'}"
        meta_label = ctk.CTkLabel(
            self, text=meta_text, font=ctk.CTkFont(size=12),
            text_color=("gray40", "gray70"), anchor="w",
        )
        meta_label.grid(row=1, column=1, sticky="w", pady=(0, 10))

        self.grid_columnconfigure(1, weight=1)

        # 카드 어디를 클릭해도 상세로 이동하도록, 모든 하위 위젯에 클릭 바인딩
        for widget in (self, badge, title_label, meta_label):
            widget.bind("<Button-1>", self._handle_click)
            widget.configure(cursor="hand2")

    def _handle_click(self, _event=None):
        if self.on_click:
            self.on_click(self.activity.id)
