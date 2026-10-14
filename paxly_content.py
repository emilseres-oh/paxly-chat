"""Dokumentkonstanter och säker formatering av Paxly-innehåll."""

from __future__ import annotations

import html
import re


SUPPORT_DOC_IDS = (
    "1qCOWysw_B6KDsCT7jPh4Aa9R_1CD5WFk53A4vgTb0JI",
    "15Mg6bJGO9viBxYF6fnBM5hehf9spUXpjbVevoWBEldk",
    "13Vw5RUvLFzST8JL5nIXyRHUULL6mvhD4pq6Y6AdE3Mg",
)
ONBOARDING_DOC_ID = SUPPORT_DOC_IDS[2]


def build_system_instruction(documents: list[str]) -> str:
    sections = "\n\n".join(
        f"--- DOKUMENT {index} ---\n{document}"
        for index, document in enumerate(documents, start=1)
    )
    return f"""
Du är en kortfattad supportassistent för bokningssystemet Paxly.
Svara alltid på svenska och använd en vänlig, tydlig och professionell ton.
Utgå bara från dokumentationen när frågan gäller Paxly. Om svaret inte finns där,
säg att du inte vet i stället för att gissa.

Paxly är indelat i två delar: publik portal och admin-portal. I den publika portalen
bokar kunder tider. I admin-portalen hanterar administratörer resurser, bokningar och
inställningar. Admin har tre lägen: hem, konfiguration och inställningar.

{sections}
""".strip()


def format_doc_to_html(text: str) -> str:
    """Konvertera onboarding-text till enkel, escaped HTML."""
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    output: list[str] = []
    in_ordered_list = False

    for index, line in enumerate(lines):
        if "paxly onboarding" in line.lower():
            continue

        if re.match(r"^\d+\.\s+", line):
            if not in_ordered_list:
                output.append("<ol>")
                in_ordered_list = True
            item = re.sub(r"^\d+\.\s+", "", line)
            output.append(f"<li>{html.escape(item)}</li>")
            continue

        if in_ordered_list:
            output.append("</ol>")
            in_ordered_list = False

        next_is_numbered = index + 1 < len(lines) and bool(
            re.match(r"^\d+\.\s+", lines[index + 1])
        )
        escaped_line = html.escape(line.lstrip("#").strip())
        tag = "h2" if next_is_numbered or line.startswith("#") else "p"
        output.append(f"<{tag}>{escaped_line}</{tag}>")

    if in_ordered_list:
        output.append("</ol>")

    return "".join(output)
