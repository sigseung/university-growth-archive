"""
views/sidebar.py

좌측 사이드바. 화면 전환 버튼들과 다크모드 토글을 담당합니다.
Sidebar는 화면 전환 '요청'만 하고(콜백 호출), 실제 화면 전환 로직은
main_window.py 가 가지고 있습니다. (Sidebar가 다른 View들을 직접 몰라야
나중에 메뉴 구성을 바꾸기 쉽습니다.)
"""

import customtkinter as ctk

# V1~V3에서 구현하는 메뉴만 활성화하고, 나머지는 로드맵에 따라 V4~V5에서 추가합니다.
MENU_ITEMS = [
    ("dashboard", "🏠  대시보드"),
    ("activities", "📋  활동"),
    ("goals", "🎯  목표"),
    ("schedule", "📅  일정"),
    ("stats", "📊  통계"),
    ("cover_letter", "📝  자소서"),
    # 아래는 V4 이후 순차 활성화 예정 (로드맵 참고)
    # ("timeline", "🕒  타임라인"),
    # ("interview", "🎤  면접"),
    # ("ai_analysis", "🤖  AI 분석"),
]


class Sidebar(ctk.CTkFrame):
    def __init__(self, master, on_navigate, on_toggle_theme, **kwargs):
        super().__init__(master, width=200, corner_radius=0, **kwargs)
        self.on_navigate = on_navigate
        self.on_toggle_theme = on_toggle_theme
        self.grid_propagate(False)

        self.logo_label = ctk.CTkLabel(
            self, text="UGA", font=ctk.CTkFont(size=22, weight="bold")
        )
        self.logo_label.pack(padx=20, pady=(24, 4), anchor="w")

        self.sub_label = ctk.CTkLabel(
            self, text="University Growth Archive",
            font=ctk.CTkFont(size=11), text_color=("gray40", "gray70"),
        )
        self.sub_label.pack(padx=20, pady=(0, 24), anchor="w")

        self.menu_buttons: dict[str, ctk.CTkButton] = {}
        for key, label in MENU_ITEMS:
            btn = ctk.CTkButton(
                self, text=label, anchor="w", fg_color="transparent",
                text_color=("gray10", "gray90"), hover_color=("gray85", "gray25"),
                command=lambda k=key: self._handle_click(k),
            )
            btn.pack(fill="x", padx=12, pady=4)
            self.menu_buttons[key] = btn

        # 하단 다크모드 토글은 pack의 side="bottom"으로 항상 아래 고정
        self.theme_switch = ctk.CTkSwitch(
            self, text="다크모드", command=self._handle_theme_toggle
        )
        self.theme_switch.pack(side="bottom", padx=20, pady=20, anchor="w")
        self.theme_switch.select()  # 기본값: 다크모드 켜짐

    def _handle_click(self, key: str):
        self.set_active(key)
        self.on_navigate(key)

    def _handle_theme_toggle(self):
        is_dark = self.theme_switch.get() == 1
        self.on_toggle_theme("dark" if is_dark else "light")

    def set_active(self, key: str):
        """현재 선택된 메뉴만 강조 표시."""
        for k, btn in self.menu_buttons.items():
            if k == key:
                btn.configure(fg_color=("gray80", "gray30"))
            else:
                btn.configure(fg_color="transparent")
