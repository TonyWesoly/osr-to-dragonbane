#!/usr/bin/env python3
"""Impozycja bookletu zeszytowego (saddle-stitch) oraz pomiar realnych rozmiarów
czcionek w pt z finalnego PDF (na potrzeby Doradcy Druku / print_guide.md).

Użycie:
  1. Impozycja bookletu + raport fontów:
     .venv/bin/python scripts/impose_booklet.py impose reading.pdf -o booklet.pdf --sheet auto
  2. Sam audyt fontów i wymiarów finalnego PDF:
     .venv/bin/python scripts/impose_booklet.py inspect reading.pdf --json-out font_audit.json
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

import pymupdf as fitz  # PyMuPDF

PT_TO_MM = 25.4 / 72.0
MM_TO_PT = 72.0 / 25.4

# Arkusze poziome (width_mm, height_mm) dla 2-up bookletu
SHEET_SIZES_MM = {
    "A4": (297.0, 210.0),    # pod strony A5 (148×210 mm)
    "A3": (420.0, 297.0),    # pod strony A4 (210×297 mm)
    "SRA4": (320.0, 225.0),  # pod A5 ze spadem 3 mm
    "SRA3": (450.0, 320.0),  # pod A4 ze spadem 3 mm
}


def pt_to_mm(v: float) -> float:
    return round(v * PT_TO_MM, 2)


def inspect_pdf_fonts(pdf_path: Path) -> dict:
    """Mierzy realne rozmiary czcionek w pt (ważone liczbą znaków) w wynikowym PDF."""
    doc = fitz.open(pdf_path)
    num_pages = len(doc)
    size_chars: Counter[float] = Counter()
    font_size_chars: Counter[tuple[str, float]] = Counter()
    page_sizes_mm: Counter[tuple[float, float]] = Counter()
    embedded_fonts: dict[str, dict] = {}

    for page in doc:
        page_sizes_mm[(pt_to_mm(page.rect.width), pt_to_mm(page.rect.height))] += 1
        for f_info in page.get_fonts(full=True):
            # (xref, ext, type, basefont, name, encoding, referencer)
            basefont = f_info[3]
            ext = f_info[1]
            embedded_fonts[basefont] = {"ext": ext, "type": f_info[2], "embedded": bool(ext)}

        d = page.get_text("dict", flags=fitz.TEXTFLAGS_TEXT)
        for b in d.get("blocks", []):
            if b.get("type") != 0:
                continue
            for ln in b.get("lines", []):
                for sp in ln.get("spans", []):
                    txt = sp.get("text", "").strip()
                    if not txt:
                        continue
                    sz = round(float(sp.get("size", 0.0)), 1)
                    fname = sp.get("font", "")
                    count = len(txt)
                    size_chars[sz] += count
                    font_size_chars[(fname, sz)] += count

    total_chars = sum(size_chars.values())
    sorted_by_freq = size_chars.most_common()
    body_size_pt = sorted_by_freq[0][0] if sorted_by_freq else 0.0

    # Wylicz percentyle rozmiarów znaków (np. p10 = przybliżony rozmiar tabel/przypisów)
    expanded_sizes = sorted(size_chars.items())
    p05 = p10 = p50 = body_size_pt
    if total_chars > 0:
        acc = 0
        got05 = got10 = got50 = False
        for sz, cnt in expanded_sizes:
            acc += cnt
            frac = acc / total_chars
            if not got05 and frac >= 0.05:
                p05 = sz
                got05 = True
            if not got10 and frac >= 0.10:
                p10 = sz
                got10 = True
            if not got50 and frac >= 0.50:
                p50 = sz
                got50 = True

    min_size_pt = min(size_chars.keys()) if size_chars else 0.0
    max_size_pt = max(size_chars.keys()) if size_chars else 0.0
    dom_page_w, dom_page_h = page_sizes_mm.most_common(1)[0][0] if page_sizes_mm else (0.0, 0.0)

    # Rekomendacja Doradcy Druku wg references/02_tlumaczenie_dtp_i_druk.md
    if dom_page_w <= 155 and dom_page_h <= 220:
        if body_size_pt >= 8.5 and num_pages <= 64:
            advisory = "Booklet A5 (druk na A4 poziomo, złożony na pół) — optymalna czytelność."
        elif body_size_pt >= 8.0 and num_pages <= 64:
            advisory = "Booklet A5 (druk na A4 poziomo) — skład zwarty (8,0–8,4 pt), nadal czytelny."
        elif num_pages > 64:
            advisory = "Objętość > 64 str. — zalecany podział na 2 booklety lub druk dwustronny 1:1 w skoroszycie."
        else:
            advisory = "UWAGA: font główny < 8,0 pt! Rozważ powiększenie fontu lub format Booklet A4 (druk na A3 poziomo)."
    else:
        advisory = (
            "Booklet A4 (druk na A3 poziomo w punkcie druku) lub alternatywnie druk domowy A4 dwustronnie 1:1 "
            "z wersji reading.pdf."
        )

    return {
        "file": str(pdf_path),
        "page_count": num_pages,
        "is_multiple_of_4": (num_pages % 4 == 0),
        "dominant_page_mm": {"width_mm": dom_page_w, "height_mm": dom_page_h},
        "total_chars": total_chars,
        "body_font_size_pt": body_size_pt,
        "median_font_size_pt": p50,
        "small_text_p10_pt": p10,
        "smallest_p05_pt": p05,
        "min_font_size_pt": min_size_pt,
        "max_font_size_pt": max_size_pt,
        "size_histogram": [
            {"size_pt": sz, "chars": cnt, "pct": round(cnt * 100.0 / max(total_chars, 1), 1)}
            for sz, cnt in sorted_by_freq[:12]
        ],
        "top_font_styles": [
            {"font": f, "size_pt": sz, "chars": cnt}
            for (f, sz), cnt in font_size_chars.most_common(12)
        ],
        "embedded_fonts": embedded_fonts,
        "all_fonts_embedded": all(v["embedded"] for v in embedded_fonts.values()),
        "print_advisor_summary": advisory,
    }


def saddle_stitch_order(num_pages: int) -> list[tuple[int, int]]:
    """Zwraca listę par (lewa_strona_1based, prawa_strona_1based) dla impozycji zeszytowej.

    Każdy arkusz fizyczny ma 2 strony PDF w booklecie: awers (przód) i rewers (tył).
    Dla N=8: [(8, 1), (2, 7), (6, 3), (4, 5)].
    """
    if num_pages <= 0 or num_pages % 4 != 0:
        raise ValueError(f"Liczba stron ({num_pages}) musi być dodatnią wielokrotnością 4.")

    pairs: list[tuple[int, int]] = []
    sheets = num_pages // 4
    for s in range(sheets):
        # Awers (przód arkusza)
        front_left = num_pages - 2 * s
        front_right = 1 + 2 * s
        pairs.append((front_left, front_right))
        # Rewers (tył arkusza, druk dwustronny Flip on short edge)
        back_left = 2 + 2 * s
        back_right = num_pages - 1 - 2 * s
        pairs.append((back_left, back_right))
    return pairs


def draw_crop_marks(page: fitz.Page, trim_rect: fitz.Rect, mark_len_mm: float = 4.0, offset_mm: float = 2.0) -> None:
    """Rysuje cienkie znaczniki cięcia wokół obszaru netto 2-up (dla arkuszy SRA4/SRA3)."""
    ml = mark_len_mm * MM_TO_PT
    off = offset_mm * MM_TO_PT
    shape = page.new_shape()
    x0, y0, x1, y1 = trim_rect.x0, trim_rect.y0, trim_rect.x1, trim_rect.y1
    xm = (x0 + x1) / 2.0

    # Narożniki
    corners = [
        ((x0 - off - ml, y0), (x0 - off, y0)),
        ((x0, y0 - off - ml), (x0, y0 - off)),
        ((x1 + off, y0), (x1 + off + ml, y0)),
        ((x1, y0 - off - ml), (x1, y0 - off)),
        ((x0 - off - ml, y1), (x0 - off, y1)),
        ((x0, y1 + off), (x0, y1 + off + ml)),
        ((x1 + off, y1), (x1 + off + ml, y1)),
        ((x1, y1 + off), (x1, y1 + off + ml)),
        # Znacznik grzbietu (bigowania)
        ((xm, y0 - off - ml), (xm, y0 - off)),
        ((xm, y1 + off), (xm, y1 + off + ml)),
    ]
    for p1, p2 in corners:
        shape.draw_line(fitz.Point(*p1), fitz.Point(*p2))
    shape.finish(color=(0, 0, 0), width=0.35)
    shape.commit()


def cmd_impose(args: argparse.Namespace) -> int:
    in_pdf = Path(args.input).resolve()
    out_pdf = Path(args.output).resolve()
    out_pdf.parent.mkdir(parents=True, exist_ok=True)

    src = fitz.open(in_pdf)
    num_pages = len(src)

    if num_pages % 4 != 0:
        print(
            f"BŁĄD: Plik wejściowy ma {num_pages} stron (nie jest wielokrotnością 4)!\n"
            "Dodaj parzystą liczbę stron wyrównujących (wyłącznie wielorazowe pomoce MG: ściągawkę procedur/zdarzeń, indeks lub czystą mapę dla graczy) "
            "PRZED wewnętrzną tylną okładką w HTML, aby zachować parzystość rozkładówek i okładek.",
            file=sys.stderr,
        )
        return 1

    # Sprawdź rozmiar strony wejściowej
    pw_pt = src[0].rect.width
    ph_pt = src[0].rect.height
    pw_mm = pt_to_mm(pw_pt)
    ph_mm = pt_to_mm(ph_pt)

    if args.sheet == "auto":
        sheet_key = "A4" if (pw_mm <= 152 and ph_mm <= 214) else "A3"
    else:
        sheet_key = args.sheet

    sw_mm, sh_mm = SHEET_SIZES_MM[sheet_key]
    sw_pt, sh_pt = sw_mm * MM_TO_PT, sh_mm * MM_TO_PT

    # Oblicz skalę (1.0 jeśli 2 strony mieszczą się na arkuszu bez pomniejszania!)
    half_sw_pt = sw_pt / 2.0
    scale = min(1.0, half_sw_pt / pw_pt, sh_pt / ph_pt)
    if args.allow_upscale:
        scale = min(half_sw_pt / pw_pt, sh_pt / ph_pt)

    placed_w = pw_pt * scale
    placed_h = ph_pt * scale

    # Wyśrodkowanie 2-up na arkuszu (obie strony stykają się dokładnie na linii grzbietu sw_pt/2)
    spine_x = sw_pt / 2.0
    top_y = (sh_pt - placed_h) / 2.0
    left_rect = fitz.Rect(spine_x - placed_w, top_y, spine_x, top_y + placed_h)
    right_rect = fitz.Rect(spine_x, top_y, spine_x + placed_w, top_y + placed_h)
    trim_rect = fitz.Rect(left_rect.x0, top_y, right_rect.x1, top_y + placed_h)

    pairs = saddle_stitch_order(num_pages)
    out = fitz.open()

    for left_p, right_p in pairs:
        sheet = out.new_page(width=sw_pt, height=sh_pt)
        sheet.show_pdf_page(left_rect, src, left_p - 1, keep_proportion=True)
        sheet.show_pdf_page(right_rect, src, right_p - 1, keep_proportion=True)
        if args.crop_marks:
            draw_crop_marks(sheet, trim_rect)

    out.save(out_pdf, garbage=4, deflate=True)
    out.close()
    src.close()

    # Audyt fontów w reading i w booklecie
    audit_in = inspect_pdf_fonts(in_pdf)
    audit_out = inspect_pdf_fonts(out_pdf)

    print(f"Utworzono booklet: {out_pdf}")
    print(f"  Strony wejściowe: {num_pages} ({pw_mm}×{ph_mm} mm) -> Arkusze fizyczne: {num_pages // 4} ({len(pairs)} stron PDF)")
    print(f"  Arkusz docelowy: {sheet_key} ({sw_mm}×{sh_mm} mm), skala impozycji: {scale * 100:.2f}%")
    print(f"  Kolejność stron (L|P): {', '.join(f'[{l}|{r}]' for l, r in pairs)}")
    print(
        f"  Realny font główny: {audit_in['body_font_size_pt']} pt "
        f"(w booklecie: {audit_out['body_font_size_pt']} pt) | "
        f"drobny/tabele p10: {audit_out['small_text_p10_pt']} pt"
    )
    print(f"  Wszystkie fonty osadzone: {audit_out['all_fonts_embedded']}")
    print(f"  Doradca Druku: {audit_in['print_advisor_summary']}")

    if args.json_out:
        payload = {
            "imposition": {
                "sheet": sheet_key,
                "sheet_mm": [sw_mm, sh_mm],
                "scale_pct": round(scale * 100.0, 2),
                "physical_sheets": num_pages // 4,
                "pairs": pairs,
                "crop_marks": bool(args.crop_marks),
            },
            "reading_audit": audit_in,
            "booklet_audit": audit_out,
        }
        Path(args.json_out).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    return 0


def cmd_inspect(args: argparse.Namespace) -> int:
    pdf_path = Path(args.input).resolve()
    audit = inspect_pdf_fonts(pdf_path)
    print(f"Audyt PDF: {pdf_path.name}")
    print(f"  Strony: {audit['page_count']} (wielokrotność 4: {audit['is_multiple_of_4']})")
    print(f"  Wymiary: {audit['dominant_page_mm']['width_mm']}×{audit['dominant_page_mm']['height_mm']} mm")
    print(
        f"  Czcionka główna: {audit['body_font_size_pt']} pt | mediana: {audit['median_font_size_pt']} pt | "
        f"p10 (tabele/przypisy): {audit['small_text_p10_pt']} pt | min/max: {audit['min_font_size_pt']}/{audit['max_font_size_pt']} pt"
    )
    print(f"  Wszystkie fonty osadzone: {audit['all_fonts_embedded']}")
    print("  Rozkład rozmiarów (top 6):")
    for row in audit["size_histogram"][:6]:
        print(f"    {row['size_pt']:>4.1f} pt — {row['pct']:>5.1f}% ({row['chars']} znaków)")
    print(f"  Doradca Druku: {audit['print_advisor_summary']}")

    if args.json_out:
        Path(args.json_out).write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Impozycja bookletu zeszytowego i pomiar czcionek w pt.")
    sub = p.add_subparsers(dest="cmd", required=True)

    p_imp = sub.add_parser("impose", help="Złóż 1-up PDF w booklet zeszytowy.")
    p_imp.add_argument("input", help="Wejściowy PDF 1-up (reading.pdf).")
    p_imp.add_argument("-o", "--output", required=True, help="Wyjściowy PDF bookletu.")
    p_imp.add_argument(
        "--sheet",
        choices=["auto", "A4", "A3", "SRA4", "SRA3"],
        default="auto",
        help="Format arkusza druku (domyślnie auto: A4 dla A5, A3 dla A4).",
    )
    p_imp.add_argument("--crop-marks", action="store_true", help="Dodaj znaczniki cięcia i bigowania.")
    p_imp.add_argument("--allow-upscale", action="store_true", help="Pozwól powiększać strony mniejsze od połowy arkusza.")
    p_imp.add_argument("--json-out", help="Zapisz pełny raport impozycji i fontów do JSON.")
    p_imp.set_defaults(func=cmd_impose)

    p_ins = sub.add_parser("inspect", help="Zmierz realne rozmiary fontów w pt i osadzenie w PDF.")
    p_ins.add_argument("input", help="Plik PDF do inspekcji.")
    p_ins.add_argument("--json-out", help="Zapisz raport do JSON.")
    p_ins.set_defaults(func=cmd_inspect)

    return p


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
