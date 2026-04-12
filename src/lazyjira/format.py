"""ADF ↔ Markdown / plain-text conversion utilities."""

from __future__ import annotations

import re
from typing import Any


def markdown_to_adf(md: str) -> dict[str, Any]:
    """Convert Markdown text to Atlassian Document Format (ADF).

    Supports: tables, headings, bullet/ordered lists, code blocks,
    bold, italic, inline code, and links.
    """

    def _inline_parse(text: str) -> list[dict]:
        nodes: list[dict] = []
        pattern = re.compile(
            r"`([^`]+)`"  # inline code
            r"|\*\*(.+?)\*\*"  # bold
            r"|(?<!\*)\*([^*]+)\*(?!\*)"  # italic *
            r"|_([^_]+)_"  # italic _
            r"|\[([^\]]+)\]\(([^)]+)\)"  # link
        )
        pos = 0
        for m in pattern.finditer(text):
            if m.start() > pos:
                nodes.append({"type": "text", "text": text[pos : m.start()]})
            if m.group(1) is not None:
                nodes.append({"type": "text", "text": m.group(1), "marks": [{"type": "code"}]})
            elif m.group(2) is not None:
                nodes.append({"type": "text", "text": m.group(2), "marks": [{"type": "strong"}]})
            elif m.group(3) is not None:
                nodes.append({"type": "text", "text": m.group(3), "marks": [{"type": "em"}]})
            elif m.group(4) is not None:
                nodes.append({"type": "text", "text": m.group(4), "marks": [{"type": "em"}]})
            elif m.group(5) is not None:
                nodes.append(
                    {
                        "type": "text",
                        "text": m.group(5),
                        "marks": [{"type": "link", "attrs": {"href": m.group(6)}}],
                    }
                )
            pos = m.end()
        if pos < len(text):
            nodes.append({"type": "text", "text": text[pos:]})
        if not nodes:
            nodes.append({"type": "text", "text": text})
        return nodes

    def _make_paragraph(text: str) -> dict:
        return {"type": "paragraph", "content": _inline_parse(text)}

    def _parse_table(lines: list[str]) -> dict:
        rows = []
        for i, line in enumerate(lines):
            stripped = line.strip().strip("|")
            cells = [c.strip() for c in stripped.split("|")]
            if all(re.match(r"^[-:]+$", c) for c in cells):
                continue
            cell_type = "tableHeader" if i == 0 else "tableCell"
            row_cells = [
                {"type": cell_type, "content": [_make_paragraph(cell)]} for cell in cells
            ]
            rows.append({"type": "tableRow", "content": row_cells})
        return {"type": "table", "content": rows}

    lines = md.split("\n")
    content: list[dict] = []
    i = 0
    while i < len(lines):
        line = lines[i]

        # Code block
        if line.strip().startswith("```"):
            lang = line.strip()[3:].strip()
            code_lines: list[str] = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code_lines.append(lines[i])
                i += 1
            i += 1
            node: dict = {
                "type": "codeBlock",
                "content": [{"type": "text", "text": "\n".join(code_lines)}],
            }
            if lang:
                node["attrs"] = {"language": lang}
            content.append(node)
            continue

        # Table
        if line.strip().startswith("|"):
            table_lines: list[str] = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                table_lines.append(lines[i])
                i += 1
            content.append(_parse_table(table_lines))
            continue

        # Heading
        hm = re.match(r"^(#{1,6})\s+(.+)$", line)
        if hm:
            level = len(hm.group(1))
            content.append(
                {"type": "heading", "attrs": {"level": level}, "content": _inline_parse(hm.group(2))}
            )
            i += 1
            continue

        # Bullet list
        if re.match(r"^[\s]*[-*]\s+", line):
            items: list[dict] = []
            while i < len(lines) and re.match(r"^[\s]*[-*]\s+", lines[i]):
                text = re.sub(r"^[\s]*[-*]\s+", "", lines[i])
                items.append({"type": "listItem", "content": [_make_paragraph(text)]})
                i += 1
            content.append({"type": "bulletList", "content": items})
            continue

        # Ordered list
        if re.match(r"^[\s]*\d+\.\s+", line):
            items = []
            while i < len(lines) and re.match(r"^[\s]*\d+\.\s+", lines[i]):
                text = re.sub(r"^[\s]*\d+\.\s+", "", lines[i])
                items.append({"type": "listItem", "content": [_make_paragraph(text)]})
                i += 1
            content.append({"type": "orderedList", "content": items})
            continue

        # Empty line
        if not line.strip():
            i += 1
            continue

        # Paragraph
        content.append(_make_paragraph(line))
        i += 1

    return {"type": "doc", "version": 1, "content": content or [_make_paragraph("")]}


def adf_to_text(adf: dict) -> str:
    """Convert Atlassian Document Format to plain text."""
    if not isinstance(adf, dict):
        return str(adf)

    texts: list[str] = []
    for block in adf.get("content", []):
        block_type = block.get("type", "")
        if block_type in ("paragraph", "heading"):
            for inline in block.get("content", []):
                if inline.get("type") == "text":
                    texts.append(inline.get("text", ""))
                elif inline.get("type") == "inlineCard":
                    texts.append(inline.get("attrs", {}).get("url", ""))
            texts.append("\n")
        elif block_type == "bulletList":
            for item in block.get("content", []):
                texts.append(f"• {adf_to_text(item).strip()}\n")
        elif block_type == "orderedList":
            for idx, item in enumerate(block.get("content", []), 1):
                texts.append(f"{idx}. {adf_to_text(item).strip()}\n")
        elif block_type == "codeBlock":
            for inline in block.get("content", []):
                if inline.get("type") == "text":
                    texts.append(f"```\n{inline.get('text', '')}\n```\n")
        elif block_type == "listItem":
            texts.append(adf_to_text(block))
        elif block_type == "table":
            for row in block.get("content", []):
                cells = [adf_to_text(cell).strip() for cell in row.get("content", [])]
                texts.append(" | ".join(cells) + "\n")
        elif block_type == "blockquote":
            texts.append("> " + adf_to_text(block).strip() + "\n")
        else:
            if "content" in block:
                texts.append(adf_to_text(block))

    return "".join(texts)
