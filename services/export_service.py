"""
services/export_service.py

활동 하나를 Markdown 또는 PDF 파일로 내보냅니다.

Markdown Export: GitHub 포트폴리오에 그대로 붙여넣을 수 있는 형태로 만듭니다.
PDF Export: reportlab으로 직접 문서를 그립니다. 한글 폰트를 등록해야
    한글이 깨지지 않으므로, utils/font_utils.py로 찾은 폰트를 등록해서 사용합니다.
    (폰트를 하나도 못 찾으면 한글이 네모로 나올 수 있다는 경고를 남깁니다.)
"""

from datetime import datetime
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from config import EXPORTS_DIR
from models.activity import Activity
from utils.font_utils import find_korean_font_path

_FONT_NAME = "UGA-Korean"
_FONT_REGISTERED = False


def _ensure_korean_font_registered() -> str:
    """reportlab에 한글 폰트를 등록하고 폰트 이름을 반환합니다.
    한 번 등록되면 재사용합니다 (매번 등록하면 느려지고, 중복 등록은 에러가 남)."""
    global _FONT_REGISTERED
    if _FONT_REGISTERED:
        return _FONT_NAME

    font_path = find_korean_font_path(exclude_collections=True)
    if font_path:
        try:
            pdfmetrics.registerFont(TTFont(_FONT_NAME, font_path))
            _FONT_REGISTERED = True
            return _FONT_NAME
        except Exception:
            pass

    # 폰트를 못 찾았거나 등록에 실패하면 기본 폰트로 폴백 (한글이 깨질 수 있음)
    return "Helvetica"


def _safe_filename(text: str) -> str:
    """파일명에 쓸 수 없는 문자를 제거."""
    invalid = '<>:"/\\|?*'
    return "".join(c for c in text if c not in invalid).strip() or "activity"


class ExportService:
    """세션이 필요 없는 순수 변환 로직이라 session을 받지 않습니다.
    (Activity 객체 하나를 이미 로딩한 상태로 넘겨받아 파일로 바꾸기만 합니다.)"""

    # ---------- Markdown ----------

    def export_to_markdown(self, activity: Activity) -> str:
        lines = [
            f"# {activity.title}",
            "",
            f"- **종류**: {activity.activity_type.value}",
            f"- **날짜**: {activity.date_start}"
            + (f" ~ {activity.date_end}" if activity.date_end else ""),
            f"- **장소**: {activity.location or '-'}",
            f"- **주최**: {activity.organizer or '-'}",
            f"- **상태**: {activity.status.value}",
            f"- **중요도**: {'★' * activity.importance}{'☆' * (5 - activity.importance)}",
        ]

        if activity.tags:
            lines.append(f"- **태그**: {', '.join('#' + t.name for t in activity.tags)}")
        if activity.categories:
            lines.append(f"- **자소서 분류**: {', '.join(c.name for c in activity.categories)}")

        lines.append("")

        for title, content in [
            ("참여 목적", activity.purpose),
            ("활동 내용", activity.content),
            ("새롭게 배운 기술", activity.new_skills),
            ("새롭게 알게 된 직무", activity.new_roles),
        ]:
            if content:
                lines += [f"## {title}", "", content, ""]

        if activity.reflections:
            lines.append("## Reflection")
            lines.append("")
            for r in activity.reflections:
                if r.learned:
                    lines.append(f"- **느낀 점**: {r.learned}")
                if r.next_action:
                    lines.append(f"- **앞으로 할 행동**: {r.next_action}")
            lines.append("")

        lines.append(f"---\n*Exported from University Growth Archive · {datetime.now().strftime('%Y-%m-%d')}*")

        content_text = "\n".join(lines)

        filename = f"{_safe_filename(activity.title)}_{activity.date_start}.md"
        out_path = Path(EXPORTS_DIR) / filename
        out_path.write_text(content_text, encoding="utf-8")
        return str(out_path)

    # ---------- PDF ----------

    def export_to_pdf(self, activity: Activity, mode: str = "portfolio") -> str:
        """mode: 'portfolio'(기본 상세) | 'star' (STAR 중심) — V4에서 STAR 필드가
        생기면 'star' 모드를 채울 예정. 지금은 portfolio 모드만 완전히 지원합니다."""
        font_name = _ensure_korean_font_registered()

        filename = f"{_safe_filename(activity.title)}_{activity.date_start}.pdf"
        out_path = Path(EXPORTS_DIR) / filename

        doc = SimpleDocTemplate(
            str(out_path), pagesize=A4,
            topMargin=20 * mm, bottomMargin=20 * mm, leftMargin=20 * mm, rightMargin=20 * mm,
        )

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "KoreanTitle", parent=styles["Title"], fontName=font_name, fontSize=20, leading=24,
        )
        heading_style = ParagraphStyle(
            "KoreanHeading", parent=styles["Heading2"], fontName=font_name, fontSize=13,
            spaceBefore=12, spaceAfter=6, textColor=colors.HexColor("#1F2937"),
        )
        body_style = ParagraphStyle(
            "KoreanBody", parent=styles["Normal"], fontName=font_name, fontSize=10.5, leading=16,
        )
        meta_style = ParagraphStyle(
            "KoreanMeta", parent=styles["Normal"], fontName=font_name, fontSize=9.5,
            leading=14, textColor=colors.HexColor("#6B7280"),
        )

        elements = [Paragraph(activity.title, title_style), Spacer(1, 8)]

        meta_rows = [
            ["종류", activity.activity_type.value, "상태", activity.status.value],
            ["날짜", str(activity.date_start), "장소", activity.location or "-"],
            ["주최", activity.organizer or "-", "중요도", "★" * activity.importance],
        ]
        meta_table = Table(meta_rows, colWidths=[28 * mm, 55 * mm, 28 * mm, 55 * mm])
        meta_table.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (-1, -1), font_name),
            ("FONTSIZE", (0, 0), (-1, -1), 9.5),
            ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#6B7280")),
            ("TEXTCOLOR", (2, 0), (2, -1), colors.HexColor("#6B7280")),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("LINEBELOW", (0, 0), (-1, -1), 0.4, colors.HexColor("#E5E7EB")),
        ]))
        elements += [meta_table, Spacer(1, 10)]

        if activity.tags or activity.categories:
            tag_text = " ".join(f"#{t.name}" for t in activity.tags)
            cat_text = "  ·  ".join(c.name for c in activity.categories)
            combined = "  ".join(x for x in [tag_text, cat_text] if x)
            elements += [Paragraph(combined, meta_style), Spacer(1, 10)]

        for heading, content in [
            ("참여 목적", activity.purpose),
            ("활동 내용", activity.content),
            ("새롭게 배운 기술", activity.new_skills),
            ("새롭게 알게 된 직무", activity.new_roles),
        ]:
            if content:
                elements += [
                    Paragraph(heading, heading_style),
                    Paragraph(content.replace("\n", "<br/>"), body_style),
                ]

        if activity.reflections:
            elements.append(Paragraph("Reflection", heading_style))
            for r in activity.reflections:
                if r.learned:
                    elements.append(Paragraph(f"<b>느낀 점</b> · {r.learned}", body_style))
                if r.next_action:
                    elements.append(Paragraph(f"<b>앞으로 할 행동</b> · {r.next_action}", body_style))
                elements.append(Spacer(1, 4))

        elements += [
            Spacer(1, 16),
            Paragraph(
                f"Exported from University Growth Archive · {datetime.now().strftime('%Y-%m-%d')}",
                meta_style,
            ),
        ]

        doc.build(elements)
        return str(out_path)
