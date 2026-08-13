"""
views/stats_view.py

통계 화면. 상단 요약 카드 + 4개 그래프(연도별/월별/종류별 비율/누적 추이)로 구성됩니다.
Matplotlib Figure를 FigureCanvasTkAgg로 감싸서 CustomTkinter 프레임 안에 넣습니다.
"""

from datetime import date

import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from database.db_session import get_session
from services.activity_service import ActivityService
from analytics import stats_calculator as calc
from analytics import chart_builder as chart


class StatsView(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.selected_year = date.today().year
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=24, pady=(20, 4))
        ctk.CTkLabel(
            header, text="통계", font=ctk.CTkFont(size=20, weight="bold")
        ).pack(side="left")

        self.summary_label = ctk.CTkLabel(
            self, text="", font=ctk.CTkFont(size=13), text_color=("gray40", "gray70"), anchor="w"
        )
        self.summary_label.pack(fill="x", padx=24, pady=(0, 12))

        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True, padx=24, pady=(0, 20))

        # 2x2 그리드로 그래프 4개 배치
        self.scroll.grid_columnconfigure((0, 1), weight=1, uniform="chart")

        self.year_chart_box = self._make_chart_box(self.scroll)
        self.year_chart_box.grid(row=0, column=0, padx=(0, 8), pady=(0, 16), sticky="nsew")

        self.month_chart_box = self._make_chart_box(self.scroll)
        self.month_chart_box.grid(row=0, column=1, padx=(8, 0), pady=(0, 16), sticky="nsew")

        self.type_chart_box = self._make_chart_box(self.scroll)
        self.type_chart_box.grid(row=1, column=0, padx=(0, 8), pady=(0, 16), sticky="nsew")

        self.trend_chart_box = self._make_chart_box(self.scroll)
        self.trend_chart_box.grid(row=1, column=1, padx=(8, 0), pady=(0, 16), sticky="nsew")

    def _make_chart_box(self, parent) -> ctk.CTkFrame:
        # 차트의 고정 배경색(analytics/chart_builder.CARD_BG)과 카드 프레임 색을
        # 맞춰서, 차트 캔버스 가장자리에 다른 색 테두리가 비치지 않도록 합니다.
        box = ctk.CTkFrame(parent, corner_radius=12, fg_color=chart.CARD_BG)
        return box

    def refresh(self):
        with get_session() as session:
            activities = ActivityService(session).list_activities()

        if not activities:
            self.summary_label.configure(text="아직 기록된 활동이 없어 통계를 표시할 수 없습니다.")
            return

        summary = calc.completion_summary(activities)
        most_type = calc.most_active_type(activities)
        self.summary_label.configure(
            text=(
                f"전체 {len(activities)}개  ·  완료 {summary.get('완료', 0)}  ·  "
                f"진행중 {summary.get('진행중', 0)}  ·  예정 {summary.get('예정', 0)}"
                + (f"  ·  가장 많이 참여한 분야: {most_type}" if most_type else "")
            )
        )

        self._render_chart(self.year_chart_box, chart.build_year_bar_chart(calc.count_by_year(activities)))

        month_counts = calc.count_by_month(activities, self.selected_year)
        self._render_chart(
            self.month_chart_box, chart.build_month_bar_chart(month_counts, self.selected_year)
        )

        self._render_chart(self.type_chart_box, chart.build_type_pie_chart(calc.count_by_type(activities)))

        self._render_chart(
            self.trend_chart_box, chart.build_growth_line_chart(calc.growth_trend_by_month(activities))
        )

    def _render_chart(self, container: ctk.CTkFrame, figure):
        for widget in container.winfo_children():
            widget.destroy()
        canvas = FigureCanvasTkAgg(figure, master=container)
        canvas.draw()
        widget = canvas.get_tk_widget()
        widget.configure(bg=chart.CARD_BG, highlightthickness=0)
        widget.pack(fill="both", expand=True, padx=8, pady=8)
