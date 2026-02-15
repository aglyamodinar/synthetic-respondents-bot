from __future__ import annotations

from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


def build_report_pdf(
    *,
    path: Path,
    study_id: str,
    run_id: str,
    language: str,
    rows: list[dict],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(path), pagesize=A4)
    width, height = A4

    y = height - 40
    c.setFont("Helvetica-Bold", 14)
    c.drawString(40, y, "Synthetic Research Report (MVP)")
    y -= 18
    c.setFont("Helvetica", 10)
    c.drawString(40, y, f"Study: {study_id} | Run: {run_id} | Language: {language}")
    y -= 16
    c.drawString(40, y, "Synthetic Research - Uncalibrated Beta")
    y -= 20

    headers = "stimulus_id | segment | mean | median | sd | T2B | B2B | TB"
    c.setFont("Helvetica-Bold", 9)
    c.drawString(40, y, headers)
    y -= 14
    c.setFont("Helvetica", 9)

    for row in rows:
        line = (
            f"{row['stimulus_id']} | {row['segment_key']} | {row['mean']:.2f} | {row['median']:.2f} | "
            f"{row['sd']:.2f} | {row['top2box']:.2%} | {row['bottom2box']:.2%} | {row['topbox']:.2%}"
        )
        c.drawString(40, y, line[:130])
        y -= 12
        if y < 50:
            c.showPage()
            y = height - 40
            c.setFont("Helvetica", 9)

    c.save()

