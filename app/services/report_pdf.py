from __future__ import annotations

from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import simpleSplit
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


def _register_unicode_font() -> tuple[str, str]:
    regular_name = "Helvetica"
    bold_name = "Helvetica-Bold"
    font_path = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
    if not font_path.exists():
        return regular_name, bold_name
    try:
        pdfmetrics.registerFont(TTFont("DejaVuSans", str(font_path)))
        return "DejaVuSans", "DejaVuSans"
    except Exception:
        return regular_name, bold_name


def _draw_wrapped(c: canvas.Canvas, text: str, x: int, y: int, width: int, font: str, size: int) -> int:
    c.setFont(font, size)
    lines = simpleSplit(text, font, size, width)
    for line in lines:
        c.drawString(x, y, line)
        y -= size + 2
    return y


def build_report_pdf(
    *,
    path: Path,
    study_id: str,
    run_id: str,
    language: str,
    question_text: str,
    model_name: str,
    respondent_count: int,
    estimated_cost_usd: float,
    rows: list[dict],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(path), pagesize=A4)
    font_regular, font_bold = _register_unicode_font()
    _, height = A4

    y = height - 40
    c.setFont(font_bold, 14)
    c.drawString(40, y, "Synthetic Research Report (MVP)")
    y -= 18
    c.setFont(font_regular, 10)
    c.drawString(
        40,
        y,
        f"Study: {study_id} | Run: {run_id} | Language: {language} | Model: {model_name}",
    )
    y -= 14
    c.drawString(40, y, f"Respondents per stimulus: {respondent_count} | Estimated Cost: ${estimated_cost_usd:.4f}")
    y -= 16
    c.drawString(40, y, "Synthetic Research - Uncalibrated Beta")
    y -= 8
    y = _draw_wrapped(c, f"Question: {question_text}", 40, y, 510, font_regular, 9)
    y -= 8

    for row in rows:
        if y < 140:
            c.showPage()
            y = height - 40

        c.setFont(font_bold, 10)
        c.drawString(40, y, f"Stimulus {row['stimulus_id']} | Segment: {row['segment_key']}")
        y -= 12
        c.setFont(font_regular, 9)
        c.drawString(
            40,
            y,
            (
                f"Mean={row['mean']:.2f}  Median={row['median']:.2f}  SD={row['sd']:.2f}  "
                f"Variance={row['variance']:.2f}  Mode={row['mode']:.0f}"
            ),
        )
        y -= 12
        c.drawString(
            40,
            y,
            (
                f"T2B={row['top2box']:.2%}  B2B={row['bottom2box']:.2%}  "
                f"TopBox={row['topbox']:.2%}  NetScore={row['net_score']:.2%}"
            ),
        )
        y -= 12
        c.drawString(
            40,
            y,
            (
                f"CI Mean=[{row['ci_mean_low']:.2f}, {row['ci_mean_high']:.2f}]  "
                f"CI T2B=[{row['ci_t2b_low']:.2%}, {row['ci_t2b_high']:.2%}]"
            ),
        )
        y -= 12
        dist = row["distribution"]
        c.drawString(
            40,
            y,
            (
                f"Distribution: 1={dist.get('1', 0.0):.2%}, 2={dist.get('2', 0.0):.2%}, "
                f"3={dist.get('3', 0.0):.2%}, 4={dist.get('4', 0.0):.2%}, 5={dist.get('5', 0.0):.2%}"
            ),
        )
        y -= 16

    c.save()
