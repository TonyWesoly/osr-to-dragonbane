#!/usr/bin/env python3
"""Szybkie wyszukiwanie w polskich podręcznikach referencyjnych Dragonbane.

Obsługuje:
- reference/podrecznik_glowny.md (ograniczone do STRONA 114; pomija Indeks na 115)
- reference/bestiariusz.md (ograniczone do STRONA 149; pomija Indeks 150 i reklamy 151–155)
- opcjonalnie reference/kopiec_witezia.md i reference/tonaca_wieza.md (--include-adventures)

Przelicza nagłówki `## STRONA X` na drukowane numery stron (`druk. str. = X - 2`).
"""

from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from dataclasses import dataclass
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
REF_DIR = ROOT_DIR / "reference"

SOURCES = {
    "pg": {
        "label": "PG",
        "full_name": "Podręcznik główny",
        "path": REF_DIR / "podrecznik_glowny.md",
        "offset": 2,
        "max_strona": 114,
    },
    "best": {
        "label": "Best.",
        "full_name": "Bestiariusz",
        "path": REF_DIR / "bestiariusz.md",
        "offset": 2,
        "max_strona": 149,
    },
}

ADVENTURE_SOURCES = {
    "kopiec": {
        "label": "Kopiec Witezia",
        "path": REF_DIR / "kopiec_witezia.md",
    },
    "wieza": {
        "label": "Tonąca Wieża",
        "path": REF_DIR / "tonaca_wieza.md",
    },
}

# Częste aliasy z angielskiego/spisów treści na kanoniczne nagłówki w tekście
ALIASES = {
    "ghoul": "ghul",
    "lindworm": "lindorm",
    "wight": "upiór",
    "ghost": "widmo",
    "skeleton": "szkielet",
    "zombie": "żywy trup",
    "fairy": "wróżka",
    "fey": "wróżka",
    "treant": "drzewiec",
    "will-o-wisp": "błędny ognik",
    "will o wisp": "błędny ognik",
    "giant spider": "ogromny pająk",
    "vampire": "wampir",
    "mummy": "mumia",
    "ooze": "ogromna ameba",
    "slime": "ogromna ameba",
    "gelatinous": "ogromna ameba",
    "stirge": "wampiroperz",
    "bat": "wampiroperz",
    "werewolf": "wilkołak",
    "gargoyle": "demon stróż",
}


def strip_diacritics(text: str) -> str:
    """Usuwa polskie znaki diakrytyczne do elastycznego dopasowania zapytań."""
    replacements = str.maketrans(
        "ąćęłńóśźżĄĆĘŁŃÓŚŹŻ",
        "acelnoszzACELNOSZZ",
    )
    text = text.translate(replacements)
    nfkd = unicodedata.normalize("NFKD", text)
    return "".join(ch for ch in nfkd if not unicodedata.combining(ch))


def norm(text: str) -> str:
    return re.sub(r"\s+", " ", strip_diacritics(text).lower()).strip()


@dataclass
class PageEntry:
    source_key: str
    label: str
    strona: int
    printed: int
    content: str


@dataclass
class SectionEntry:
    source_key: str
    label: str
    heading: str
    level: int
    strona_start: int
    printed_start: int
    strona_end: int
    printed_end: int
    body: str


def load_pages(source_key: str) -> list[PageEntry]:
    cfg = SOURCES[source_key]
    path: Path = cfg["path"]
    if not path.exists():
        raise FileNotFoundError(f"Brak pliku referencyjnego: {path}")

    raw = path.read_text(encoding="utf-8")
    parts = re.split(r"(?m)^## STRONA (\d+)\s*$", raw)
    pages: list[PageEntry] = []
    offset = cfg["offset"]
    max_strona = cfg["max_strona"]

    for i in range(1, len(parts), 2):
        strona = int(parts[i])
        if strona > max_strona:
            continue
        body = parts[i + 1].replace("<!-- PAGE_START -->", "").strip()
        pages.append(
            PageEntry(
                source_key=source_key,
                label=cfg["label"],
                strona=strona,
                printed=strona - offset,
                content=body,
            )
        )
    return pages


def extract_sections(pages: list[PageEntry]) -> list[SectionEntry]:
    """Dzieli strony na sekcje wg nagłówków Markdown (### i ####)."""
    sections: list[SectionEntry] = []
    current: dict | None = None

    def flush():
        nonlocal current
        if current is not None:
            sections.append(
                SectionEntry(
                    source_key=current["source_key"],
                    label=current["label"],
                    heading=current["heading"],
                    level=current["level"],
                    strona_start=current["strona_start"],
                    printed_start=current["printed_start"],
                    strona_end=current["strona_end"],
                    printed_end=current["printed_end"],
                    body="\n".join(current["lines"]).strip(),
                )
            )
            current = None

    for page in pages:
        for line in page.content.splitlines():
            m = re.match(r"^(#{3,4})\s+(.+?)\s*$", line)
            if m:
                level = len(m.group(1))
                heading = m.group(2).strip()
                # Pomijaj drobne śródtytuły w ramach tego samego wpisu przy łączeniu
                # Tworzymy nową sekcję dla każdego ### oraz ####
                flush()
                current = {
                    "source_key": page.source_key,
                    "label": page.label,
                    "heading": heading,
                    "level": level,
                    "strona_start": page.strona,
                    "printed_start": page.printed,
                    "strona_end": page.strona,
                    "printed_end": page.printed,
                    "lines": [line],
                }
            elif current is not None:
                current["strona_end"] = page.strona
                current["printed_end"] = page.printed
                current["lines"].append(line)
    flush()
    return sections


def expand_query(query: str) -> tuple[str, str | None]:
    q_norm = norm(query)
    if q_norm in ALIASES:
        return ALIASES[q_norm], f"(alias: '{query}' -> '{ALIASES[q_norm]}')"
    return query, None


def cmd_page(source_keys: list[str], printed_pages: list[int]) -> int:
    found = 0
    for key in source_keys:
        pages = {p.printed: p for p in load_pages(key)}
        for pp in printed_pages:
            if pp in pages:
                p = pages[pp]
                print(f"=== {p.label} str. {p.printed} [STRONA {p.strona}] ===")
                print(p.content)
                print()
                found += 1
            else:
                print(f"[Brak] {SOURCES[key]['label']} str. {pp} (poza zakresem merytorycznym)", file=sys.stderr)
    return 0 if found else 1


def cmd_heading(source_keys: list[str], query: str, full_entry: bool, max_chars: int) -> int:
    effective_query, note = expand_query(query)
    if note:
        print(note, file=sys.stderr)
    q_norm = norm(effective_query)

    matches: list[tuple[int, SectionEntry, list[PageEntry]]] = []

    for key in source_keys:
        pages = load_pages(key)
        sections = extract_sections(pages)
        for idx, sec in enumerate(sections):
            h_norm = norm(sec.heading)
            score = 0
            if h_norm == q_norm:
                score = 100
            elif h_norm.startswith(q_norm):
                score = 80
            elif q_norm in h_norm:
                score = 60
            if score > 0:
                # Jeśli dopasowano ###, dołącz podsekcje #### aż do kolejnego ###
                if full_entry and sec.level == 3:
                    merged_lines = [sec.body]
                    end_s = sec.strona_end
                    end_p = sec.printed_end
                    for nxt in sections[idx + 1 :]:
                        if nxt.level <= 3:
                            break
                        merged_lines.append(nxt.body)
                        end_s = nxt.strona_end
                        end_p = nxt.printed_end
                    merged = SectionEntry(
                        source_key=sec.source_key,
                        label=sec.label,
                        heading=sec.heading,
                        level=sec.level,
                        strona_start=sec.strona_start,
                        printed_start=sec.printed_start,
                        strona_end=end_s,
                        printed_end=end_p,
                        body="\n\n".join(merged_lines),
                    )
                    matches.append((score, merged, pages))
                else:
                    matches.append((score, sec, pages))

    matches.sort(key=lambda x: (-x[0], x[1].source_key, x[1].printed_start))

    if not matches:
        print(f"Nie znaleziono nagłówka pasującego do: {effective_query!r}", file=sys.stderr)
        return 1

    for _, sec, _ in matches:
        page_range = (
            f"str. {sec.printed_start}"
            if sec.printed_start == sec.printed_end
            else f"str. {sec.printed_start}–{sec.printed_end}"
        )
        strona_range = (
            f"STRONA {sec.strona_start}"
            if sec.strona_start == sec.strona_end
            else f"STRONA {sec.strona_start}–{sec.strona_end}"
        )
        print(f"=== {sec.label} {page_range} [{strona_range}] — {sec.heading} ===")
        body = sec.body
        if max_chars > 0 and len(body) > max_chars:
            body = body[:max_chars].rstrip() + f"\n... [obcięto do {max_chars} znaków; użyj --max-chars 0 dla całości]"
        print(body)
        print()
    return 0


def cmd_search(
    source_keys: list[str],
    query: str,
    context_lines: int,
    limit: int,
    include_adventures: bool,
) -> int:
    effective_query, note = expand_query(query)
    if note:
        print(note, file=sys.stderr)
    q_norm = norm(effective_query)

    hits = 0
    for key in source_keys:
        pages = load_pages(key)
        for page in pages:
            lines = page.content.splitlines()
            matched_indices: list[int] = []
            for idx, line in enumerate(lines):
                if q_norm in norm(line):
                    matched_indices.append(idx)
            if not matched_indices:
                continue

            # Zgrupuj sąsiednie trafienia w bloki kontekstowe
            blocks: list[tuple[int, int]] = []
            for idx in matched_indices:
                start = max(0, idx - context_lines)
                end = min(len(lines) - 1, idx + context_lines)
                if blocks and start <= blocks[-1][1] + 1:
                    blocks[-1] = (blocks[-1][0], max(blocks[-1][1], end))
                else:
                    blocks.append((start, end))

            # Znajdź ostatni nagłówek przed pierwszym trafieniem na stronie
            heading_ctx = ""
            for h_idx in range(matched_indices[0], -1, -1):
                if lines[h_idx].startswith("###"):
                    heading_ctx = f" ({lines[h_idx].lstrip('#').strip()})"
                    break

            for start, end in blocks:
                hits += 1
                print(f"--- {page.label} str. {page.printed} [STRONA {page.strona}]{heading_ctx} ---")
                for ln in lines[start : end + 1]:
                    print(ln)
                print()
                if limit and hits >= limit:
                    print(f"[Osiągnięto limit {limit} trafień; zwiększ przez --limit]", file=sys.stderr)
                    return 0

    if include_adventures:
        for adv_key, cfg in ADVENTURE_SOURCES.items():
            path: Path = cfg["path"]
            if not path.exists():
                continue
            lines = path.read_text(encoding="utf-8").splitlines()
            for idx, line in enumerate(lines):
                if q_norm in norm(line):
                    hits += 1
                    start = max(0, idx - context_lines)
                    end = min(len(lines) - 1, idx + context_lines)
                    print(f"--- {cfg['label']} (linia {idx + 1}) ---")
                    for ln in lines[start : end + 1]:
                        print(ln)
                    print()
                    if limit and hits >= limit:
                        return 0

    if hits == 0:
        print(f"Brak wyników dla: {effective_query!r}", file=sys.stderr)
        return 1
    return 0


def cmd_list_headings(source_keys: list[str], level_filter: int | None) -> int:
    for key in source_keys:
        pages = load_pages(key)
        sections = extract_sections(pages)
        print(f"=== Nagłówki: {SOURCES[key]['full_name']} ({SOURCES[key]['label']}) ===")
        for sec in sections:
            if level_filter and sec.level != level_filter:
                continue
            indent = "  " * (sec.level - 3)
            print(f"{indent}- {sec.heading} — {sec.label} str. {sec.printed_start} [STRONA {sec.strona_start}]")
        print()
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Punktowe wyszukiwanie w polskich podręcznikach referencyjnych Dragonbane (z drukowaną numeracją stron)."
    )
    p.add_argument("query", nargs="?", help="Szukana fraza (lub nazwa potwora/czaru/zasady).")
    p.add_argument(
        "-s",
        "--source",
        choices=["pg", "best", "both"],
        default="both",
        help="Źródło: pg (Podręcznik główny), best (Bestiariusz), both (oba, domyślnie).",
    )
    p.add_argument(
        "-H",
        "--heading",
        action="store_true",
        help="Szukaj po nagłówkach i zwróć całą sekcję (idealne dla potworów, czarów i zasad).",
    )
    p.add_argument(
        "--shallow",
        action="store_true",
        help="Przy --heading nie dołączaj podsekcji ####.",
    )
    p.add_argument(
        "-p",
        "--page",
        type=int,
        nargs="+",
        help="Wyświetl konkretne DRUKOWANE numery stron (np. --source pg --page 97).",
    )
    p.add_argument(
        "--list-headings",
        action="store_true",
        help="Wylistuj nagłówki ###/#### z drukowanymi numerami stron.",
    )
    p.add_argument(
        "--level",
        type=int,
        choices=[3, 4],
        help="Filtr poziomu nagłówka przy --list-headings.",
    )
    p.add_argument(
        "-C",
        "--context",
        type=int,
        default=2,
        help="Liczba linii kontekstu przy wyszukiwaniu pełnotekstowym (domyślnie 2).",
    )
    p.add_argument(
        "--limit",
        type=int,
        default=20,
        help="Maks. liczba trafień przy wyszukiwaniu pełnotekstowym (0 = bez limitu, domyślnie 20).",
    )
    p.add_argument(
        "--max-chars",
        type=int,
        default=8000,
        help="Maks. długość pojedynczej sekcji przy --heading (0 = bez limitu, domyślnie 8000).",
    )
    p.add_argument(
        "--include-adventures",
        action="store_true",
        help="Uwzględnij też kopiec_witezia.md i tonaca_wieza.md w wyszukiwaniu pełnotekstowym.",
    )
    return p


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    source_keys = ["pg", "best"] if args.source == "both" else [args.source]

    if args.page:
        return cmd_page(source_keys, args.page)
    if args.list_headings:
        return cmd_list_headings(source_keys, args.level)
    if not args.query:
        parser.print_help()
        return 2
    if args.heading:
        return cmd_heading(source_keys, args.query, full_entry=not args.shallow, max_chars=args.max_chars)
    return cmd_search(
        source_keys,
        args.query,
        context_lines=args.context,
        limit=args.limit,
        include_adventures=args.include_adventures,
    )


if __name__ == "__main__":
    raise SystemExit(main())
