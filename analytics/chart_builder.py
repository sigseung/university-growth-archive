"""
analytics/chart_builder.py

stats_calculator.py가 계산한 숫자를 받아서 Matplotlib Figure로 그려주는 곳입니다.
Figure를 만들기만 하고, 화면에 붙이는 건 views/stats_view.py가 담당합니다
(FigureCanvasTkAgg로 CustomTkinter 위젯 안에 삽입).

다크모드 대응: CustomTkinter가 다크/라이트 모드를 지원하므로,
그래프도 배경을 투명하게 만들고 텍스트 색은 밝은 회색으로 통일해서
다크모드에서 어색하지 않게 했습니다. (라이트모드에서도 그런대로 읽힙니다.)
"""

import matplotlib
matplotlib.use("Agg")  # Tkinter 캔버스에 그리기 전 렌더링 백엔드 (GUI 스레드와 충돌 방지)

import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from utils.font_utils import find_korean_font_path

_FONT_APPLIED = False


def _apply_korean_font():
    """앱 전체에서 한 번만 폰트를 설정합니다 (매번 그래프 그릴 때마다 하면 느려짐)."""
    global _FONT_APPLIED
    if _FONT_APPLIED:
        return
    font_path = find_korean_font_path()
    if font_path:
        from matplotlib import font_manager

        font_manager.fontManager.addfont(font_path)
        font_name = font_manager.FontProperties(fname=font_path).get_name()
        plt.rcParams["font.family"] = font_name
    plt.rcParams["axes.unicode_minus"] = False  # 마이너스 기호 깨짐 방지
    _FONT_APPLIED = True


# 다크모드 UI와 어울리는 색상 팔레트 (활동 종류 색상과 통일감을 주기 위해
# views/components/card.py의 type_colors와 계열을 맞췄습니다)
PALETTE = [
    "#3B82F6", "#F59E0B", "#10B981", "#EF4444", "#8B5CF6",
    "#06B6D4", "#EC4899", "#F97316", "#84CC16", "#6366F1", "#14B8A6",
]


def _new_figure(figsize=(6, 3.4)) -> tuple[Figure, "plt.Axes"]:
    _apply_korean_font()
    fig = Figure(figsize=figsize, dpi=100)
    # 카드 배경과 자연스럽게 이어지도록, 투명이 아니라 카드와 같은 짙은 슬레이트 색을
    # '고정으로' 칠합니다. (다크/라이트 모드를 앱에서 토글할 수 있지만,
    # 그래프 자체는 항상 짙은 배경 카드 위에 올라간다는 전제로 통일했습니다.
    # → FigureCanvasTkAgg는 완전 투명 배경을 지원하지 않아, 투명 처리 시
    #    캔버스 기본색인 흰색이 그대로 비쳐 보이는 문제가 있었습니다.)
    card_bg = "#1F2937"
    fig.patch.set_facecolor(card_bg)
    ax = fig.add_subplot(111)
    ax.set_facecolor(card_bg)
    text_color = "#D1D5DB"  # 짙은 배경 위에서 잘 읽히는 밝은 회색
    ax.tick_params(colors=text_color, labelsize=9)
    for spine in ax.spines.values():
        spine.set_color("#4B5563")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    return fig, ax


CARD_BG = "#1F2937"


def build_year_bar_chart(year_counts: dict[int, int]) -> Figure:
    """연도별 활동 수 막대 그래프."""
    fig, ax = _new_figure()
    years = list(year_counts.keys())
    values = list(year_counts.values())
    ax.bar([str(y) for y in years], values, color=PALETTE[0], width=0.5)
    ax.set_title("연도별 활동 수", color="#D1D5DB", fontsize=11)
    for i, v in enumerate(values):
        ax.text(i, v, str(v), ha="center", va="bottom", color="#D1D5DB", fontsize=9)
    fig.tight_layout()
    return fig


def build_month_bar_chart(month_counts: dict[int, int], year: int) -> Figure:
    """특정 연도의 월별 활동 수 막대 그래프."""
    fig, ax = _new_figure()
    months = list(month_counts.keys())
    values = list(month_counts.values())
    ax.bar([f"{m}월" for m in months], values, color=PALETTE[2], width=0.6)
    ax.set_title(f"{year}년 월별 활동 수", color="#D1D5DB", fontsize=11)
    ax.tick_params(axis="x", rotation=0, labelsize=8)
    fig.tight_layout()
    return fig


def build_type_pie_chart(type_counts: dict[str, int]) -> Figure:
    """활동 종류별 비율 파이 차트."""
    fig, ax = _new_figure(figsize=(6, 3.6))
    labels = list(type_counts.keys())
    values = list(type_counts.values())
    colors = [PALETTE[i % len(PALETTE)] for i in range(len(labels))]

    wedges, _texts, autotexts = ax.pie(
        values, labels=None, autopct="%1.0f%%", colors=colors, pctdistance=0.75,
        textprops={"color": "white", "fontsize": 9}, radius=1.1,
    )
    ax.legend(
        wedges, labels, loc="center left", bbox_to_anchor=(1.02, 0.5),
        fontsize=9, labelcolor="#D1D5DB", frameon=False, borderaxespad=0,
    )
    ax.set_title("활동 종류별 비율", color="#D1D5DB", fontsize=11)
    # 범례가 그림 밖으로 잘리지 않도록 오른쪽 여백을 넉넉히 남깁니다.
    fig.subplots_adjust(left=0.05, right=0.68, top=0.88, bottom=0.05)
    return fig


def build_growth_line_chart(trend: list[tuple[str, int]]) -> Figure:
    """전체 기간 누적 활동 수 추이 라인 그래프 ('성장 추이')."""
    fig, ax = _new_figure()
    if not trend:
        ax.text(0.5, 0.5, "데이터가 없습니다", ha="center", va="center", color="#9CA3AF")
        return fig

    labels = [t[0] for t in trend]
    values = [t[1] for t in trend]
    ax.plot(labels, values, color=PALETTE[4], marker="o", markersize=3, linewidth=2)
    ax.fill_between(range(len(labels)), values, color=PALETTE[4], alpha=0.15)
    ax.set_title("누적 성장 추이", color="#D1D5DB", fontsize=11)

    # x축 라벨이 너무 많으면 겹치므로, 최대 8개까지만 보이도록 간격을 둡니다.
    step = max(1, len(labels) // 8)
    ax.set_xticks(range(0, len(labels), step))
    ax.set_xticklabels([labels[i] for i in range(0, len(labels), step)], rotation=40, ha="right", fontsize=8)
    fig.tight_layout()
    return fig
