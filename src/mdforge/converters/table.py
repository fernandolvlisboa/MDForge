from collections.abc import Iterable, Sequence


def cell_to_text(value: object) -> str:
    if value is None:
        return ""
    text = str(value).strip().replace("\r\n", "\n").replace("\r", "\n")
    text = " ".join(part.strip() for part in text.splitlines() if part.strip())
    return text.replace("|", "\\|")


def clean_table_rows(rows: Iterable[Sequence[object]]) -> list[list[str]]:
    cleaned = [[cell_to_text(cell) for cell in row] for row in rows]
    cleaned = [row for row in cleaned if any(row)]
    if not cleaned:
        return []

    width = max(len(row) for row in cleaned)
    cleaned = [row + [""] * (width - len(row)) for row in cleaned]

    while width > 1 and all(not row[-1] for row in cleaned):
        for row in cleaned:
            row.pop()
        width -= 1

    return cleaned


def table_to_markdown(
    rows: Iterable[Sequence[object]], *, extract_caption: bool = False
) -> str:
    cleaned = clean_table_rows(rows)
    if not cleaned:
        return ""

    captions: list[str] = []
    if extract_caption and len(cleaned[0]) > 1:
        while len(cleaned) > 1:
            filled = [cell for cell in cleaned[0] if cell]
            if len(filled) != 1:
                break
            captions.append(filled[0])
            cleaned.pop(0)

    if not cleaned:
        return "\n\n".join(f"**{caption}**" for caption in captions)

    width = max(len(row) for row in cleaned)
    cleaned = [row + [""] * (width - len(row)) for row in cleaned]
    header = cleaned[0]
    body = cleaned[1:]
    lines = [
        "| " + " | ".join(header) + " |",
        "| " + " | ".join(["---"] * width) + " |",
    ]
    lines.extend("| " + " | ".join(row) + " |" for row in body)
    table = "\n".join(lines)

    if not captions:
        return table
    return "\n\n".join([*(f"**{caption}**" for caption in captions), table])
