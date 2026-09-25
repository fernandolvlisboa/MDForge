from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from statistics import median
from typing import TYPE_CHECKING, Any

import pdfplumber
from pypdf import PdfReader

from .base import Converter
from .table import table_to_markdown

if TYPE_CHECKING:
    from ..models import ConversionOptions


@dataclass
class _Line:
    top: float
    bottom: float
    words: list[dict[str, Any]]

    @property
    def text(self) -> str:
        return " ".join(str(word["text"]) for word in self.words).strip()


def _group_words_into_lines(
    words: list[dict[str, Any]], tolerance: float = 3.0
) -> list[_Line]:
    lines: list[_Line] = []
    for word in sorted(words, key=lambda item: (float(item["top"]), float(item["x0"]))):
        top = float(word["top"])
        if not lines or abs(top - lines[-1].top) > tolerance:
            lines.append(_Line(top=top, bottom=float(word["bottom"]), words=[word]))
        else:
            lines[-1].words.append(word)
            lines[-1].bottom = max(lines[-1].bottom, float(word["bottom"]))

    for line in lines:
        line.words.sort(key=lambda item: float(item["x0"]))
    return lines


def _infer_columns(lines: list[_Line], min_gap: float = 18.0) -> list[tuple[float, float]]:
    events: list[tuple[float, float]] = []
    for line in lines:
        for left, right in zip(line.words, line.words[1:]):
            gap = float(right["x0"]) - float(left["x1"])
            if gap >= min_gap:
                events.append((float(left["x1"]), float(right["x0"])))

    if not events:
        return []

    clusters: list[list[tuple[float, float]]] = []
    for event in sorted(events, key=lambda pair: pair[1]):
        if not clusters:
            clusters.append([event])
            continue

        center = median(pair[1] for pair in clusters[-1])
        if abs(event[1] - center) <= 18.0:
            clusters[-1].append(event)
        else:
            clusters.append([event])

    min_occurrences = max(3, round(len(lines) * 0.2))
    useful = [cluster for cluster in clusters if len(cluster) >= min_occurrences]

    columns: list[tuple[float, float]] = []
    for cluster in useful:
        successor_x = median(pair[1] for pair in cluster)
        boundary = median((left + right) / 2 for left, right in cluster)
        columns.append((boundary, successor_x))
    return columns[:5]


def _line_to_cells(line: _Line, columns: list[tuple[float, float]]) -> list[str]:
    if not columns:
        return [line.text]

    boundaries = [item[0] for item in columns]
    successors = [item[1] for item in columns]
    cells = [[] for _ in range(len(columns) + 1)]

    first = line.words[0]
    first_center = (float(first["x0"]) + float(first["x1"])) / 2
    column = sum(first_center > boundary for boundary in boundaries)
    cells[column].append(str(first["text"]))

    for left, right in zip(line.words, line.words[1:]):
        gap = float(right["x0"]) - float(left["x1"])
        next_center = (float(right["x0"]) + float(right["x1"])) / 2
        target = sum(next_center > boundary for boundary in boundaries)
        aligned = any(abs(float(right["x0"]) - x) <= 30.0 for x in successors)

        if target > column and gap >= 18.0 and aligned:
            column = target
        cells[column].append(str(right["text"]))

    return [" ".join(parts).strip() for parts in cells]


def _find_table_blocks(page) -> tuple[list[_Line], list[tuple[int, int, list[list[str]]]]]:
    words = page.extract_words(
        x_tolerance=2, y_tolerance=3, keep_blank_chars=False
    ) or []
    lines = _group_words_into_lines(words)
    columns = _infer_columns(lines)
    if not columns:
        return lines, []

    parsed = [_line_to_cells(line, columns) for line in lines]
    structured = [sum(bool(cell) for cell in row) >= 2 for row in parsed]

    blocks: list[tuple[int, int, list[list[str]]]] = []
    start: int | None = None
    for index, is_structured in enumerate(structured + [False]):
        if is_structured and start is None:
            start = index
        elif not is_structured and start is not None:
            if index - start >= 3:
                block = parsed[start:index]
                width = max(len(row) for row in block)
                active_columns = sum(
                    any(row[column] for row in block) for column in range(width)
                )
                if active_columns >= 2:
                    blocks.append((start, index, block))
            start = None

    return lines, blocks


def _extract_page(page) -> str:
    lines, blocks = _find_table_blocks(page)
    if not blocks:
        return (page.extract_text(x_tolerance=2, y_tolerance=3) or "").strip()

    out: list[str] = []
    cursor = 0
    for start, end, rows in blocks:
        if start > cursor:
            text = "\n".join(line.text for line in lines[cursor:start]).strip()
            if text:
                out.append(text)

        markdown = table_to_markdown(rows)
        if markdown:
            out.append(markdown)
        cursor = end

    if cursor < len(lines):
        text = "\n".join(line.text for line in lines[cursor:]).strip()
        if text:
            out.append(text)

    return "\n\n".join(out).strip()


def _fallback_with_pypdf(source: Path) -> str:
    reader = PdfReader(str(source))
    chunks: list[str] = []
    for index, page in enumerate(reader.pages, start=1):
        text = (page.extract_text() or "").strip()
        chunks.append(f"## Página {index}\n\n{text if text else '*Sem texto extraível.*'}")
    return "\n\n".join(chunks).strip() + "\n"


class PdfConverter(Converter):
    extensions = (".pdf",)

    def convert(self, source: Path, options: ConversionOptions | None = None) -> str:
        try:
            chunks: list[str] = []
            with pdfplumber.open(str(source)) as pdf:
                for index, page in enumerate(pdf.pages, start=1):
                    text = _extract_page(page)
                    chunks.append(
                        f"## Página {index}\n\n{text if text else '*Sem texto extraível.*'}"
                    )
            return "\n\n".join(chunks).strip() + "\n"
        except Exception:  # noqa: BLE001 - fallback intencional para PDFs fora do layout suportado
            return _fallback_with_pypdf(source)
