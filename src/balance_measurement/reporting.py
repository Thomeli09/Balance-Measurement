"""Dependency-free Markdown / LaTeX specimen and measurement summaries."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from .analysis import Summary
from .domain import Specimen


def markdown_report(specimen: Specimen, summary: Summary) -> str:
    """Return readable text for a lab notebook without external templating libs."""
    lines = [
        f"# Measurement report — {specimen.specimen_id}", "",
        f"Generated: {datetime.now(timezone.utc).isoformat()}", "",
        f"Project: {specimen.project or 'not specified'}", "",
        f"Material: {specimen.material or 'not specified'}", "",
        f"Operator: {specimen.operator or 'not specified'}", "",
        f"Description: {specimen.description or 'not specified'}", "",
        "## Measurements", "",
        f"- Observations: {summary.count}",
        f"- Stable readings: {summary.stable_count}",
        f"- Mean: {summary.mean} {summary.unit}",
        f"- Minimum: {summary.minimum} {summary.unit}",
        f"- Maximum: {summary.maximum} {summary.unit}",
        f"- Sample standard deviation: {summary.standard_deviation} {summary.unit}"
        if summary.standard_deviation is not None else "- Sample standard deviation: n/a",
    ]
    if specimen.conditions:
        lines.extend(["", "## Conditions", ""])
        lines.extend(f"- {key}: {value}" for key, value in specimen.conditions.items())
    return "\n".join(lines) + "\n"


def escape_latex(value: object) -> str:
    """Safely escape LaTeX text supplied by users or instrument metadata."""
    escaped = {
        "\\": r"\textbackslash{}", "{": r"\{", "}": r"\}", "#": r"\#",
        "$": r"\$", "%": r"\%", "&": r"\&", "_": r"\_",
        "~": r"\textasciitilde{}", "^": r"\textasciicircum{}",
    }
    return "".join(escaped.get(character, character) for character in str(value))


def latex_report(specimen: Specimen, summary: Summary) -> str:
    """Generate a complete simple LaTeX report; compilation is up to the caller."""
    rows = [
        ("Specimen ID", specimen.specimen_id),
        ("Project", specimen.project),
        ("Material", specimen.material),
        ("Operator", specimen.operator),
        ("Description", specimen.description),
        ("Observations", summary.count),
        ("Stable observations", summary.stable_count),
        ("Mean", f"{summary.mean} {summary.unit}"),
        ("Minimum", f"{summary.minimum} {summary.unit}"),
        ("Maximum", f"{summary.maximum} {summary.unit}"),
        (
            "Std. deviation",
            summary.standard_deviation if summary.standard_deviation is not None else "n/a",
        ),
        *specimen.conditions.items(),
    ]
    body = "\n".join(
        f"{escape_latex(label)} & {escape_latex(value)} \\\\"
        for label, value in rows
    )
    return (
        r"\documentclass{article}" "\n"
        r"\usepackage[T1]{fontenc}" "\n"
        r"\usepackage[utf8]{inputenc}" "\n"
        r"\usepackage{longtable}" "\n"
        r"\begin{document}" "\n"
        r"\section*{Balance measurement report}" "\n"
        r"\begin{longtable}{ll}" "\n"
        f"{body}\n"
        r"\end{longtable}" "\n"
        r"\end{document}" "\n"
    )


def save_report(text: str, path: str | Path) -> Path:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")
    return destination
