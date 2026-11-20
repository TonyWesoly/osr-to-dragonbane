#!/usr/bin/env python3
"""Budowanie PDF z HTML+CSS (pojedynczy plik lub katalog modularnych stron work/pages/p01.html...)
przez WeasyPrint z polską typografią (DOM-safe &nbsp; i pyphen), jawnym wykrywaniem przepełnień
stron `.page` oraz lekkimi podglądami Visual QA wyłącznie w RGB JPEG (< 1 MB, max 1600 px).

Przykłady użycia:
  1. Z modularnego katalogu stron (całość lub wybrany zakres):
     .venv/bin/python scripts/build_pdf.py modules/<slug>/work/pages \
         --pages 1-15 \
         -o modules/<slug>/work/batch_01_15.pdf \
         --preview-dir modules/<slug>/work/preview_jpg \
         --compare-dir modules/<slug>/work/pages_jpg \
         --diff-dir modules/<slug>/work/compare_jpg \
         --strict
  2. Z pojedynczego pliku HTML:
     .venv/bin/python scripts/build_pdf.py modules/<slug>/work/module.html \
         -o modules/<slug>/output/<slug>_reading.pdf --strict
"""

from __future__ import annotations

import argparse
import io
import os
import re
import sys
from pathlib import Path

import numpy as np
import pymupdf as fitz  # PyMuPDF
from bs4 import BeautifulSoup, Comment, NavigableString
from PIL import Image, ImageFilter
from weasyprint import CSS, HTML

NBSP = "\u00a0"
SKIP_TAGS = {"script", "style", "code", "pre", "title", "textarea", "svg", "math"}
BW_ALGO_VERSION = "bw_v1"

RE_HEX_COLOR = re.compile(r"^#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})$")
RE_STYLE_COLOR = re.compile(r"\b(fill|stroke)\s*:\s*(#[0-9a-fA-F]{3,6})\b", re.IGNORECASE)

# Twarde limity podglądów Visual QA (ochrona przed HTTP 400 INVALID_MEDIA)
DEFAULT_PREVIEW_DPI = 150
DEFAULT_PREVIEW_MAX_SIDE = 1600
DEFAULT_PREVIEW_QUALITY = 82
HARD_MAX_PREVIEW_BYTES = 980_000  # bezpiecznie poniżej 1 MB (1 000 000 B)

# Reguły wstawiania twardej spacji wyłącznie w węzłach tekstowych DOM
RE_SINGLE_LETTER = re.compile(r"(?<![A-Za-zĄĆĘŁŃÓŚŹŻąćęłńóśźż0-9])([aiouwzAIOUWZ]) (?=\S)")
RE_ABBREV = re.compile(r"\b(str\.|poz\.|pot\.|nr|ryc\.|rys\.|tab\.|rozdz\.|ok\.|tj\.|tzn\.) (?=\S)", re.IGNORECASE)
RE_UNITS = re.compile(
    r"(\b(?:\d*k\d+(?:[+-]\d+)?|\d+(?:[.,–-]\d+)?))\s+"
    r"(m|cm|mm|km|g|kg|s|min|h|WT|SW|złota|srebra|miedzi|zł|sr|md|szt\.|pkt|rund\w*|kwadrans\w*|kwart\w*|poziom\w*|kręgu|krąg)"
    r"(?![A-Za-zĄĆĘŁŃÓŚŹŻąćęłńóśźż0-9])"
)
RE_EN_DASH = re.compile(r" (–|—) ")
RE_REF_BOOK = re.compile(r"\b(PG|Best\.) (?=str\.)", re.IGNORECASE)

RE_PAGE_NUM = re.compile(r"(\d+)")


def to_rgb_image(im: Image.Image) -> Image.Image:
    """Konwertuje obraz Pillow do czystego RGB (spłaszczając ewentualną alfę na białe tło)."""
    if im.mode == "RGB":
        return im
    if im.mode in ("RGBA", "LA") or (im.mode == "P" and "transparency" in im.info):
        rgba = im.convert("RGBA")
        bg = Image.new("RGB", rgba.size, (255, 255, 255))
        bg.paste(rgba, mask=rgba.getchannel("A"))
        return bg
    return im.convert("RGB")


def save_preview_jpeg(
    im: Image.Image,
    out_path: Path,
    max_side: int = DEFAULT_PREVIEW_MAX_SIDE,
    quality: int = DEFAULT_PREVIEW_QUALITY,
    max_bytes: int = HARD_MAX_PREVIEW_BYTES,
) -> tuple[Path, int, tuple[int, int]]:
    """Zapisuje lekki podgląd RGB JPEG do Visual QA (max 1600 px, jakość ~82%, twardy limit < 1 MB)."""
    out_path = out_path.with_suffix(".jpg")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    work = to_rgb_image(im)
    w, h = work.size
    longest = max(w, h)
    if longest > max_side:
        scale = max_side / float(longest)
        work = work.resize((max(1, int(round(w * scale))), max(1, int(round(h * scale)))), Image.Resampling.LANCZOS)

    cur_im = work
    for _scale_step in range(5):
        for q in (quality, 76, 70, 64, 58, 50):
            if q > quality:
                continue
            buf = io.BytesIO()
            cur_im.save(
                buf,
                format="JPEG",
                quality=q,
                optimize=True,
                progressive=True,
                subsampling=2,
            )
            data = buf.getvalue()
            if len(data) <= max_bytes:
                out_path.write_bytes(data)
                return out_path, len(data), cur_im.size
        nw = max(400, int(round(cur_im.width * 0.85)))
        nh = max(400, int(round(cur_im.height * 0.85)))
        cur_im = cur_im.resize((nw, nh), Image.Resampling.LANCZOS)

    buf = io.BytesIO()
    cur_im.save(buf, format="JPEG", quality=45, optimize=True, subsampling=2)
    data = buf.getvalue()
    out_path.write_bytes(data)
    return out_path, len(data), cur_im.size


def pixmap_to_pil_rgb(pix: fitz.Pixmap) -> Image.Image:
    if pix.n - pix.alpha > 3:
        pix = fitz.Pixmap(fitz.csRGB, pix)
    if pix.alpha:
        im = Image.frombytes("RGBA", (pix.width, pix.height), pix.samples)
        return to_rgb_image(im)
    return Image.frombytes("RGB", (pix.width, pix.height), pix.samples)


def parse_pages_spec(spec: str) -> set[int]:
    """Parsuje specyfikację stron typu '1-11', '1-5,12-13,16' na zbiór numerów całkowitych."""
    selected: set[int] = set()
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            lo_s, hi_s = part.split("-", 1)
            lo, hi = int(lo_s.strip()), int(hi_s.strip())
            if lo > hi:
                lo, hi = hi, lo
            selected.update(range(lo, hi + 1))
        else:
            selected.add(int(part))
    return selected


def extract_file_page_num(path: Path) -> int | None:
    m = RE_PAGE_NUM.search(path.stem)
    return int(m.group(1)) if m else None


def natural_page_sort_key(path: Path) -> tuple[int, int, str]:
    num = extract_file_page_num(path)
    return (0 if num is not None else 1, num if num is not None else 0, path.name.lower())


def extract_inner_html_if_full_doc(text: str) -> str:
    """Jeśli plik strony jest pełnym dokumentem HTML z <body>, zwraca wnętrze <body>; inaczej surowy fragment."""
    if "<body" in text.lower():
        soup = BeautifulSoup(text, "lxml")
        if soup.body is not None:
            return "".join(str(child) for child in soup.body.contents).strip()
    return text.strip()


def load_source_html(
    source_path: Path,
    pages_spec: str | None = None,
    base_dir_override: str | None = None,
    title: str | None = None,
    auto_css: bool = True,
) -> tuple[str, Path, list[int | None]]:
    """Wczytuje pojedynczy plik HTML lub automatycznie skleja katalog modularnych stron `work/pages/p01.html...`.

    Zwraca: (raw_html, base_url_dir, lista_numerow_plikow_dla_stron)
    """
    if source_path.is_file():
        base_dir = Path(base_dir_override).resolve() if base_dir_override else source_path.parent
        return source_path.read_text(encoding="utf-8"), base_dir, []

    if not source_path.is_dir():
        raise FileNotFoundError(f"Nie znaleziono źródła HTML ani katalogu stron: {source_path}")

    # Katalog modularnych stron: preferuj p*.html, a jeśli brak, wszystkie *.html
    candidates = sorted(source_path.glob("p*.html"), key=natural_page_sort_key)
    if not candidates:
        candidates = sorted(source_path.glob("*.html"), key=natural_page_sort_key)
    if not candidates:
        raise FileNotFoundError(f"Brak plików *.html w katalogu stron: {source_path}")

    selected_nums = parse_pages_spec(pages_spec) if pages_spec else None
    chosen: list[tuple[Path, int | None]] = []
    for idx, fpath in enumerate(candidates, 1):
        fnum = extract_file_page_num(fpath)
        match_num = fnum if fnum is not None else idx
        if selected_nums is None or match_num in selected_nums:
            chosen.append((fpath, match_num))

    if not chosen:
        raise ValueError(f"Żaden plik w {source_path} nie pasuje do filtra --pages {pages_spec!r}")

    base_dir = Path(base_dir_override).resolve() if base_dir_override else source_path.parent
    css_link = ""
    if auto_css and (base_dir / "style.css").exists():
        css_link = '\n  <link rel="stylesheet" href="style.css">'

    doc_title = title or f"{base_dir.parent.name} — Dragonbane PL"
    chunks: list[str] = []
    file_nums: list[int | None] = []
    for fpath, num in chosen:
        inner = extract_inner_html_if_full_doc(fpath.read_text(encoding="utf-8"))
        chunks.append(f"<!-- ===== STRONA MODULARNA: {fpath.name} ===== -->\n{inner}")
        file_nums.append(num)

    wrapped = (
        "<!DOCTYPE html>\n"
        '<html lang="pl">\n'
        "<head>\n"
        '  <meta charset="utf-8">\n'
        f"  <title>{doc_title}</title>{css_link}\n"
        "</head>\n"
        "<body>\n\n"
        + "\n\n".join(chunks)
        + "\n\n</body>\n"
        "</html>\n"
    )
    return wrapped, base_dir, file_nums


def apply_polish_nbsp_to_text(text: str) -> str:
    """Wstawia polskie twarde spacje oraz wielokropek typograficzny w pojedynczym węźle tekstowym."""
    cur = text.replace("...", "\u2026")
    prev = None
    while cur != prev:
        prev = cur
        cur = RE_SINGLE_LETTER.sub(rf"\1{NBSP}", cur)
    cur = RE_REF_BOOK.sub(rf"\1{NBSP}", cur)
    cur = RE_ABBREV.sub(rf"\1{NBSP}", cur)
    cur = RE_UNITS.sub(rf"\1{NBSP}\2", cur)
    cur = RE_EN_DASH.sub(rf"{NBSP}\1 ", cur)
    return cur


def parse_hex_rgb(color_str: str) -> tuple[int, int, int] | None:
    m = RE_HEX_COLOR.match(color_str.strip())
    if not m:
        return None
    hx = m.group(1)
    if len(hx) == 3:
        return (int(hx[0] * 2, 16), int(hx[1] * 2, 16), int(hx[2] * 2, 16))
    return (int(hx[0:2], 16), int(hx[2:4], 16), int(hx[4:6], 16))


def convert_chromatic_hex_to_bw(color_str: str) -> tuple[str, bool]:
    """Konwertuje chromatyczny kolor hex (np. #3953a4) na głęboki drukarski czarny lub neutralną szarość."""
    rgb = parse_hex_rgb(color_str)
    if rgb is None:
        return color_str, False
    r, g, b = rgb
    if max(r, g, b) - min(r, g, b) <= 15:
        return color_str, False
    lum = 0.299 * r + 0.587 * g + 0.114 * b
    if lum < 155.0:
        return "#111111", True
    gv = max(0, min(245, int(round(lum))))
    return f"#{gv:02x}{gv:02x}{gv:02x}", True


def is_map_img_tag(img_tag, rel_src: str) -> bool:
    """Rozpoznaje obrazy map (kreskowych/wektorowych), których nie wolno rozmywać korekcją gamma."""
    low_src = rel_src.lower()
    if "map" in low_src:
        return True
    for node in [img_tag, *img_tag.parents]:
        if not getattr(node, "attrs", None):
            continue
        classes = " ".join(node.get("class") or []).lower()
        if any(tok in classes for tok in ("map-base", "map-stage", "map-inset", "map-wrap")):
            return True
    return False


def optimize_image_for_bw(
    src_path: Path,
    dst_path: Path,
    is_map_hint: bool = False,
    force: bool = False,
) -> tuple[bool, str]:
    """Konwertuje kolorowe ilustracje do zoptymalizowanej skali szarości pod druk laserowy B&W.

    Zwraca: (czy_zapisano_plik_bw, kategoria_przetwarzania)
    - Obrazy już monochromatyczne (mapy kreskowe L/1, szare banery) zostają nietknięte (zwraca False).
    - Ilustracje kolorowe otrzymują adaptacyjne rozjaśnienie cieni (gamma pod przyrost punktu w laserze),
      delikatny kontrast i subtelne wyostrzenie z twardą ochroną czystej bieli teł winiet.
    - Jasne ramki ozdobne na białym tle (np. bordiura strony tytułowej) są subtelnie przyciemniane,
      by nie znikały w druku B&W.
    - Logotypy z kanałem alfa (RGBA) zachowują pełną przezroczystość przy zerowej chromatyczności.
    """
    with Image.open(src_path) as im:
        has_alpha = im.mode in ("RGBA", "LA") or (im.mode == "P" and "transparency" in im.info)
        if im.mode in ("1", "L", "LA") and not is_map_hint:
            return False, "already-gray"

        if has_alpha:
            rgba = im.convert("RGBA")
            arr = np.asarray(rgba, dtype=np.float32)
            rgb = arr[:, :, :3]
            alpha = arr[:, :, 3]
            opaque_mask = alpha > 16.0
            if not np.any(opaque_mask):
                return False, "empty-alpha"
            sat_fg = rgb[:, :, :3].max(axis=2) - rgb[:, :, :3].min(axis=2)
            col_pct = float((sat_fg[opaque_mask] > 15.0).mean() * 100.0)
            if col_pct < 2.0:
                return False, "already-gray"

            if dst_path.exists() and not force and dst_path.stat().st_mtime >= src_path.stat().st_mtime:
                return True, "cached-alpha"

            lum = 0.299 * rgb[:, :, 0] + 0.587 * rgb[:, :, 1] + 0.114 * rgb[:, :, 2]
            x = np.clip(lum / 255.0, 0.0, 1.0)
            # Rozjaśnij kolorowe wypełnienia logotypów, zachowując głęboką czerń konturów
            y = np.power(x, 0.76)
            y = np.clip((y - 0.48) * 1.16 + 0.48, 0.0, 1.0)
            dark_ink = lum < 55.0
            out_l = np.clip(np.round(y * 255.0), 0, 255).astype(np.uint8)
            out_l[dark_ink] = np.clip(np.round(lum[dark_ink] * 0.75), 0, 255).astype(np.uint8)

            out_rgba = np.stack([out_l, out_l, out_l, alpha.astype(np.uint8)], axis=2)
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            Image.fromarray(out_rgba, mode="RGBA").save(dst_path, format="PNG", optimize=True)
            return True, "alpha-logo-bw"

        rgb = np.asarray(im.convert("RGB"), dtype=np.float32)
        sat = rgb.max(axis=2) - rgb.min(axis=2)
        col_pct = float((sat > 15.0).mean() * 100.0)
        if col_pct < 2.0:
            return False, "already-gray"

        if dst_path.exists() and not force and dst_path.stat().st_mtime >= src_path.stat().st_mtime:
            return True, "cached"

        lum = 0.299 * rgb[:, :, 0] + 0.587 * rgb[:, :, 1] + 0.114 * rgb[:, :, 2]
        white_pct = float((lum >= 245.0).mean() * 100.0)
        p05 = float(np.percentile(lum, 5))

        if is_map_hint:
            # Kolorowa mapa z innego modułu -> ostra skala szarości z oczyszczonym białym tłem
            orig_white = lum >= 238.0
            x = np.clip(lum / 255.0, 0.0, 1.0)
            y = np.clip((x - 0.55) * 1.18 + 0.55, 0.0, 1.0)
            out_u8 = np.clip(np.round(y * 255.0), 0, 255).astype(np.uint8)
            out_u8[orig_white] = 255
            out_im = Image.fromarray(out_u8, mode="L")
            kind = "colored-map-bw"
        elif white_pct >= 60.0 and p05 >= 195.0:
            # Jasna pastelowa bordiura/ornament na czystym białym tle (np. title_frame.png)
            bg_white = lum >= 251.0
            deepened = 255.0 - (255.0 - lum) * 1.85
            out_u8 = np.clip(np.round(deepened), 130, 250).astype(np.uint8)
            out_u8[bg_white] = 255
            out_im = Image.fromarray(out_u8, mode="L")
            kind = "highkey-ornament-bw"
        else:
            # Ilustracja kolorowa / okładka: adaptacyjne rozjaśnienie cieni + kontrast pod druk laserowy
            orig_white = (lum >= 245.0) & (sat <= 14.0)
            fg = lum[~orig_white]
            med_fg = float(np.median(fg)) if fg.size > 0 else float(np.median(lum))

            if med_fg < 65.0:
                gamma, toe = 0.54, 0.055
            elif med_fg < 105.0:
                gamma, toe = 0.65, 0.04
            else:
                gamma, toe = 0.78, 0.02

            x = np.clip(lum / 255.0, 0.0, 1.0)
            y = np.power(x, gamma)
            y = toe + (1.0 - toe) * y
            y = np.clip((y - 0.52) * 1.14 + 0.52, 0.0, 1.0)
            out_u8 = np.clip(np.round(y * 255.0), 0, 255).astype(np.uint8)
            out_u8[orig_white] = 255

            out_im = Image.fromarray(out_u8, mode="L")
            out_im = out_im.filter(ImageFilter.UnsharpMask(radius=1.0, percent=40, threshold=4))
            # Ponownie przypnij tło winiet do czystej bieli po wyostrzeniu (zero szarej ramki)
            if np.any(orig_white):
                arr_sharp = np.asarray(out_im, dtype=np.uint8).copy()
                arr_sharp[orig_white] = 255
                out_im = Image.fromarray(arr_sharp, mode="L")
            kind = f"art-bw(g={gamma:.2f},med={med_fg:.0f})"

        dst_path.parent.mkdir(parents=True, exist_ok=True)
        ext = dst_path.suffix.lower()
        if ext in (".jpg", ".jpeg"):
            out_im.save(dst_path, format="JPEG", quality=92, optimize=True)
        else:
            out_im.save(dst_path, format="PNG", optimize=True)
        return True, kind


def apply_bw_mode_to_soup(
    soup: BeautifulSoup,
    base_dir: Path,
    bw_css_path: Path | None,
    force_rebuild: bool = False,
) -> dict:
    """Przełącza dokument HTML w DOM na tryb B&W bez duplikowania plików źródłowych HTML."""
    html_tag = soup.find("html")
    if html_tag is not None:
        cls = list(html_tag.get("class") or [])
        if "bw-mode" not in cls:
            cls.append("bw-mode")
            html_tag["class"] = cls
    body_tag = soup.find("body")
    if body_tag is not None:
        cls = list(body_tag.get("class") or [])
        if "bw-mode" not in cls:
            cls.append("bw-mode")
            body_tag["class"] = cls

    # Dołącz style_bw.css w <head> zaraz po style.css (jeśli podany i istnieje)
    bw_css_href: str | None = None
    if bw_css_path is not None and bw_css_path.exists():
        head = soup.find("head")
        if head is not None:
            try:
                rel_css = os.path.relpath(bw_css_path.resolve(), base_dir.resolve()).replace("\\", "/")
            except ValueError:
                rel_css = bw_css_path.resolve().as_uri()
            link_tag = soup.new_tag("link", rel="stylesheet", href=rel_css)
            head.append(link_tag)
            bw_css_href = rel_css

    # Sprawdź wersję cache assets_bw/
    assets_bw_dir = base_dir / "assets_bw"
    ver_file = assets_bw_dir / ".bw_version"
    version_mismatch = not (ver_file.exists() and ver_file.read_text(encoding="utf-8").strip() == BW_ALGO_VERSION)
    effective_force = force_rebuild or version_mismatch

    converted_imgs: dict[str, str] = {}
    preserved_gray: set[str] = set()
    img_cache_result: dict[str, tuple[bool, str, str]] = {}

    for img in soup.find_all("img"):
        src = (img.get("src") or "").strip()
        if not src or src.startswith(("http://", "https://", "data:", "assets_bw/")):
            continue
        src_abs = (base_dir / src).resolve()
        if not src_abs.is_file():
            continue
        try:
            rel_path = src_abs.relative_to(base_dir.resolve())
        except ValueError:
            rel_path = Path(src_abs.name)

        map_hint = is_map_img_tag(img, src)
        cache_key = f"{rel_path.as_posix()}|map={map_hint}"
        if cache_key not in img_cache_result:
            dst_abs = assets_bw_dir / rel_path
            changed, kind = optimize_image_for_bw(src_abs, dst_abs, is_map_hint=map_hint, force=effective_force)
            new_rel = (Path("assets_bw") / rel_path).as_posix()
            img_cache_result[cache_key] = (changed, kind, new_rel)

        changed, kind, new_rel = img_cache_result[cache_key]
        if changed:
            img["src"] = new_rel
            converted_imgs[rel_path.as_posix()] = kind
        else:
            preserved_gray.add(rel_path.as_posix())

    if converted_imgs:
        assets_bw_dir.mkdir(parents=True, exist_ok=True)
        ver_file.write_text(BW_ALGO_VERSION + "\n", encoding="utf-8")

    # Konwersja kolorów w inline <svg> (WeasyPrint izoluje inline SVG od zewnętrznego CSS!)
    svg_recolored = 0
    for svg in soup.find_all("svg"):
        for el in [svg, *svg.find_all(True)]:
            explicit_fill = el.get("data-bw-fill")
            explicit_stroke = el.get("data-bw-stroke")
            if explicit_fill is not None:
                el["fill"] = explicit_fill
                svg_recolored += 1
            elif el.get("fill"):
                new_val, changed = convert_chromatic_hex_to_bw(str(el["fill"]))
                if changed:
                    el["fill"] = new_val
                    svg_recolored += 1

            if explicit_stroke is not None:
                el["stroke"] = explicit_stroke
                svg_recolored += 1
            elif el.get("stroke"):
                new_val, changed = convert_chromatic_hex_to_bw(str(el["stroke"]))
                if changed:
                    el["stroke"] = new_val
                    svg_recolored += 1

            if el.get("style"):
                def _repl_style(m: re.Match) -> str:
                    nonlocal svg_recolored
                    nv, ch = convert_chromatic_hex_to_bw(m.group(2))
                    if ch:
                        svg_recolored += 1
                    return f"{m.group(1)}: {nv}"

                el["style"] = RE_STYLE_COLOR.sub(_repl_style, str(el["style"]))

    return {
        "bw_css": bw_css_href,
        "converted_imgs": converted_imgs,
        "preserved_gray_imgs": sorted(preserved_gray),
        "svg_recolored": svg_recolored,
    }


def process_html_dom(
    html_text: str,
    insert_nbsp: bool = True,
    bw_mode: bool = False,
    base_dir: Path | None = None,
    bw_css_path: Path | None = None,
    bw_rebuild_assets: bool = False,
) -> tuple[str, int, list[dict], dict | None]:
    """Przetwarza HTML przez BeautifulSoup/lxml bez naruszania tagów i CSS.

    Zwraca: (przetworzony_html, liczba_elementow_page, lista_metadanych_page, raport_bw_lub_None)
    """
    soup = BeautifulSoup(html_text, "lxml")

    html_tag = soup.find("html")
    if html_tag is not None and not html_tag.get("lang"):
        html_tag["lang"] = "pl"

    if insert_nbsp:
        for node in list(soup.descendants):
            if isinstance(node, Comment):
                continue
            if isinstance(node, NavigableString):
                parent = node.parent
                if parent is None:
                    continue
                if any(p.name in SKIP_TAGS for p in [parent, *parent.parents] if getattr(p, "name", None)):
                    continue
                original = str(node)
                if not original.strip():
                    continue
                updated = apply_polish_nbsp_to_text(original)
                if updated != original:
                    node.replace_with(NavigableString(updated))

    bw_report: dict | None = None
    if bw_mode and base_dir is not None:
        bw_report = apply_bw_mode_to_soup(
            soup,
            base_dir=base_dir,
            bw_css_path=bw_css_path,
            force_rebuild=bw_rebuild_assets,
        )

    page_els = soup.select(".page")
    page_meta = []
    for idx, el in enumerate(page_els, 1):
        page_meta.append(
            {
                "index": idx,
                "id": el.get("id", ""),
                "data_page": el.get("data-page", str(idx)),
                "data_orig_page": el.get("data-orig-page", ""),
                "classes": el.get("class", []),
            }
        )

    return str(soup), len(page_els), page_meta, bw_report


def _iter_boxes(box):
    yield box
    for child in getattr(box, "children", ()) or ():
        yield from _iter_boxes(child)


def inspect_weasyprint_overflow(document, expected_pages: int) -> dict:
    """Wykrywa przepełnienia stron `.page` bez polegania na overflow: hidden."""
    rendered_pages = len(document.pages)
    issues: list[str] = []
    page_reports: list[dict] = []

    if expected_pages > 0 and rendered_pages != expected_pages:
        issues.append(
            f"NIEZGODNA LICZBA STRON: HTML zawiera {expected_pages} elementów .page, "
            f"ale WeasyPrint wyrenderował {rendered_pages} stron! "
            "(Najprawdopodobniej jedna ze stron przepełnieniem wypchnęła dodatkową stronę.)"
        )

    px_to_mm = 25.4 / 96.0

    for p_idx, page in enumerate(document.pages, 1):
        pbox = page._page_box
        page_h = pbox.height

        content_top = pbox.content_box_y()
        content_bottom = content_top + pbox.height
        content_left = pbox.content_box_x()
        content_right = content_left + pbox.width

        page_div_boxes = []
        max_child_bottom = content_top
        max_child_right = content_left
        overflow_nodes: list[dict] = []

        for b in _iter_boxes(pbox):
            el = getattr(b, "element", None)
            cls_list = []
            tag_name = ""
            if el is not None and hasattr(el, "attrib"):
                cls_list = (el.attrib.get("class") or "").split()
                tag_name = str(getattr(el, "tag", ""))

            if "page" in cls_list:
                page_div_boxes.append(b)

            if tag_name in ("html", "body") or "page" in cls_list:
                continue
            if any(c in cls_list for c in ("bleed", "full-bleed", "page-bg", "cover-bg")):
                continue
            if el is None:
                continue

            bx0 = getattr(b, "position_x", 0.0)
            by0 = getattr(b, "position_y", 0.0)
            bw = getattr(b, "margin_width", lambda: getattr(b, "width", 0.0))()
            bh = getattr(b, "margin_height", lambda: getattr(b, "height", 0.0))()
            bx1 = bx0 + bw
            by1 = by0 + bh

            if by1 > max_child_bottom:
                max_child_bottom = by1
            if bx1 > max_child_right:
                max_child_right = bx1

            bottom_over = by1 - content_bottom
            right_over = bx1 - content_right
            if bottom_over > 2.0 or right_over > 2.0:
                snippet = ""
                if hasattr(b, "text") and b.text:
                    snippet = str(b.text)[:50]
                overflow_nodes.append(
                    {
                        "tag": tag_name,
                        "classes": cls_list,
                        "bottom_overflow_mm": round(max(0.0, bottom_over) * px_to_mm, 2),
                        "right_overflow_mm": round(max(0.0, right_over) * px_to_mm, 2),
                        "text": snippet,
                    }
                )

        data_pages_on_sheet = []
        for pb in page_div_boxes:
            dp = pb.element.attrib.get("data-page") or pb.element.attrib.get("id") or ""
            if dp and dp not in data_pages_on_sheet:
                data_pages_on_sheet.append(dp)

        fill_pct = round(((max_child_bottom - content_top) / max(page_h, 1.0)) * 100.0, 1)
        rep = {
            "pdf_page": p_idx,
            "data_pages": data_pages_on_sheet,
            "page_size_mm": [round(pbox.margin_width() * px_to_mm, 1), round(pbox.margin_height() * px_to_mm, 1)],
            "vertical_fill_pct": fill_pct,
            "overflow_count": len(overflow_nodes),
            "overflow_samples": overflow_nodes[:5],
        }
        page_reports.append(rep)

        if overflow_nodes:
            max_b = max(n["bottom_overflow_mm"] for n in overflow_nodes)
            max_r = max(n["right_overflow_mm"] for n in overflow_nodes)
            issues.append(
                f"PRZEPEŁNIENIE na stronie PDF {p_idx} (data-page={data_pages_on_sheet}): "
                f"dół +{max_b} mm, prawo +{max_r} mm ({len(overflow_nodes)} boksów)."
            )

    return {
        "expected_pages": expected_pages,
        "rendered_pages": rendered_pages,
        "ok": len(issues) == 0,
        "issues": issues,
        "pages": page_reports,
    }


def render_pdf_to_previews(
    pdf_path: Path,
    preview_dir: Path,
    dpi: int,
    max_side: int = DEFAULT_PREVIEW_MAX_SIDE,
    quality: int = DEFAULT_PREVIEW_QUALITY,
    page_labels: list[int] | None = None,
) -> tuple[list[tuple[Path, int]], int]:
    """Renderuje strony wynikowego PDF wyłącznie do lekkich plików RGB JPEG (< 1 MB, max 1600 px)."""
    preview_dir.mkdir(parents=True, exist_ok=True)
    doc = fitz.open(pdf_path)
    zoom = dpi / 72.0
    mat = fitz.Matrix(zoom, zoom)
    out_items: list[tuple[Path, int]] = []
    max_bytes = 0
    for idx in range(len(doc)):
        label = page_labels[idx] if (page_labels and idx < len(page_labels)) else (idx + 1)
        pix = doc[idx].get_pixmap(matrix=mat, alpha=False)
        im = pixmap_to_pil_rgb(pix)
        out_p, nbytes, _ = save_preview_jpeg(
            im,
            preview_dir / f"page_{label:02d}.jpg",
            max_side=max_side,
            quality=quality,
        )
        max_bytes = max(max_bytes, nbytes)
        out_items.append((out_p, label))
    return out_items, max_bytes


def find_orig_preview(orig_dir: Path, orig_pno: int) -> Path | None:
    """Znajduje podgląd strony oryginału (preferuje lekki JPEG, awaryjnie PNG)."""
    for ext in (".jpg", ".jpeg", ".png"):
        cand = orig_dir / f"page_{orig_pno:02d}{ext}"
        if cand.exists():
            return cand
    return None


def resolve_orig_page_number(
    idx_1based: int,
    label_num: int,
    meta: dict | None,
    page_offset: int,
    from_modular_dir: bool,
) -> int | None:
    """Wyznacza numer strony oryginału (1-based) do porównania Visual QA lub None dla nowej strony."""
    if meta:
        raw_orig = str(meta.get("data_orig_page", "")).strip().lower()
        if raw_orig in ("none", "new", "-", "brak"):
            return None
        if raw_orig.isdigit():
            return int(raw_orig)
    if from_modular_dir:
        return label_num + page_offset
    return idx_1based + page_offset


def build_side_by_side_diffs(
    orig_dir: Path,
    pl_items: list[tuple[Path, int]],
    diff_dir: Path,
    page_meta: list[dict],
    page_offset: int = 0,
    from_modular_dir: bool = False,
    max_side: int = DEFAULT_PREVIEW_MAX_SIDE,
    quality: int = DEFAULT_PREVIEW_QUALITY,
) -> tuple[int, int]:
    """Tworzy lekkie obrazy porównawcze RGB JPEG (oryginał po lewej vs PL po prawej; max 1600 px, < 1 MB)."""
    diff_dir.mkdir(parents=True, exist_ok=True)
    created = 0
    max_bytes = 0

    for idx, (pl_path, label_num) in enumerate(pl_items, 1):
        meta = page_meta[idx - 1] if idx - 1 < len(page_meta) else None
        orig_pno = resolve_orig_page_number(idx, label_num, meta, page_offset, from_modular_dir)
        if orig_pno is None or orig_pno < 1:
            continue
        orig_path = find_orig_preview(orig_dir, orig_pno)
        if orig_path is None:
            continue

        with Image.open(orig_path) as im_o_raw, Image.open(pl_path) as im_p_raw:
            im_orig = to_rgb_image(im_o_raw)
            im_pl = to_rgb_image(im_p_raw)

            target_h = max(im_orig.height, im_pl.height)
            if im_orig.height != target_h:
                w = max(1, int(round(im_orig.width * target_h / im_orig.height)))
                im_orig = im_orig.resize((w, target_h), Image.Resampling.LANCZOS)
            if im_pl.height != target_h:
                w = max(1, int(round(im_pl.width * target_h / im_pl.height)))
                im_pl = im_pl.resize((w, target_h), Image.Resampling.LANCZOS)

            gap = 16
            canvas = Image.new("RGB", (im_orig.width + im_pl.width + gap, target_h), (210, 210, 210))
            canvas.paste(im_orig, (0, 0))
            canvas.paste(im_pl, (im_orig.width + gap, 0))

            _, nbytes, _ = save_preview_jpeg(
                canvas,
                diff_dir / f"compare_{label_num:02d}.jpg",
                max_side=max_side,
                quality=quality,
            )
            max_bytes = max(max_bytes, nbytes)
            created += 1

    return created, max_bytes


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Build HTML+CSS -> PDF (WeasyPrint) z obsługą modularnych stron work/pages/, "
        "polską typografią, kontrolą przepełnień i lekkimi podglądami Visual QA (RGB JPEG < 1 MB)."
    )
    p.add_argument(
        "source",
        help="Wejściowy plik HTML lub katalog modularnych stron (np. modules/<slug>/work/pages).",
    )
    p.add_argument("-o", "--output", required=True, help="Wynikowy plik PDF.")
    p.add_argument(
        "--pages",
        help="Filtr stron dla katalogu modularnego (np. '1-15' lub '1-5,16-17').",
    )
    p.add_argument(
        "--base-dir",
        help="Katalog bazowy dla zasobów (CSS/obrazy); dla work/pages domyślnie katalog nadrzędny work/.",
    )
    p.add_argument("--title", help="Tytuł dokumentu HTML przy sklejaniu z katalogu pages/.")
    p.add_argument("--no-auto-css", action="store_true", help="Nie dołączaj automatycznie style.css przy sklejaniu pages/.")
    p.add_argument("--css", nargs="*", default=[], help="Opcjonalne dodatkowe arkusze CSS.")
    p.add_argument(
        "--bw",
        action="store_true",
        help="Tryb czarno-biały pod druk laserowy: dołącza work/style_bw.css, optymalizuje kolorowe ilustracje do work/assets_bw/ i neutralizuje kolory inline SVG (bez duplikowania HTML).",
    )
    p.add_argument("--bw-css", help="Opcjonalna ścieżka do arkusza CSS B&W (domyślnie <base-dir>/style_bw.css).")
    p.add_argument("--bw-rebuild-assets", action="store_true", help="Wymuś ponowną konwersję grafik w work/assets_bw/.")
    p.add_argument("--no-nbsp", action="store_true", help="Wyłącz automatyczne wstawianie polskich twardych spacji.")
    p.add_argument("--dump-html", help="Zapisz sklejony i przetworzony HTML (z &nbsp;) pod wskazaną ścieżką.")
    p.add_argument(
        "--preview-dir",
        "--jpg-dir",
        "--png-dir",
        dest="preview_dir",
        help="Wyrenderuj strony wynikowego PDF jako lekkie RGB JPEG (< 1 MB, max 1600 px) do tego katalogu.",
    )
    p.add_argument("--dpi", type=int, default=DEFAULT_PREVIEW_DPI, help=f"DPI rasteryzacji podglądów (domyślnie {DEFAULT_PREVIEW_DPI}).")
    p.add_argument("--max-side", type=int, default=DEFAULT_PREVIEW_MAX_SIDE, help=f"Maks. dłuższy bok JPEG w px (domyślnie {DEFAULT_PREVIEW_MAX_SIDE}).")
    p.add_argument("--quality", type=int, default=DEFAULT_PREVIEW_QUALITY, help=f"Jakość JPEG 1–95 (domyślnie {DEFAULT_PREVIEW_QUALITY}).")
    p.add_argument("--compare-dir", help="Katalog z oryginalnymi podglądami (pages_jpg/) do porównania 1:1.")
    p.add_argument("--diff-dir", help="Katalog wyjściowy na porównania side-by-side RGB JPEG (wymaga --preview-dir i --compare-dir).")
    p.add_argument("--page-offset", type=int, default=0, help="Przesunięcie numeru strony oryginału przy porównaniu częściowym.")
    p.add_argument("--strict", action="store_true", help="Zakończ kodem wyjścia 1, jeśli wykryto jakiekolwiek przepełnienie.")
    return p


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    source_path = Path(args.source).resolve()
    from_modular_dir = source_path.is_dir()
    out_pdf = Path(args.output).resolve()
    out_pdf.parent.mkdir(parents=True, exist_ok=True)

    raw_html, base_dir, file_nums = load_source_html(
        source_path,
        pages_spec=args.pages,
        base_dir_override=args.base_dir,
        title=args.title,
        auto_css=not args.no_auto_css,
    )
    bw_css_path: Path | None = None
    if args.bw:
        if args.bw_css:
            bw_css_path = Path(args.bw_css).resolve()
            if not bw_css_path.exists():
                raise FileNotFoundError(f"Nie znaleziono wskazanego arkusza --bw-css: {bw_css_path}")
        elif not args.no_auto_css and (base_dir / "style_bw.css").exists():
            bw_css_path = (base_dir / "style_bw.css").resolve()

    processed_html, expected_pages, page_meta, bw_report = process_html_dom(
        raw_html,
        insert_nbsp=not args.no_nbsp,
        bw_mode=args.bw,
        base_dir=base_dir,
        bw_css_path=bw_css_path,
        bw_rebuild_assets=args.bw_rebuild_assets,
    )

    if args.dump_html:
        dump_p = Path(args.dump_html).resolve()
        dump_p.parent.mkdir(parents=True, exist_ok=True)
        dump_p.write_text(processed_html, encoding="utf-8")

    stylesheets = [CSS(filename=str(Path(c).resolve())) for c in args.css]
    html_obj = HTML(string=processed_html, base_url=str(base_dir))
    document = html_obj.render(stylesheets=stylesheets)

    report = inspect_weasyprint_overflow(document, expected_pages)
    document.write_pdf(str(out_pdf))

    print(f"Zbudowano PDF: {out_pdf}")
    if from_modular_dir:
        print(f"  Źródło modularne: {source_path} ({len(file_nums)} plików stron)")
    if bw_report is not None:
        print(
            f"  Tryb B&W (--bw): CSS={bw_report['bw_css'] or 'brak'} | "
            f"grafiki zoptymalizowane do assets_bw/: {len(bw_report['converted_imgs'])} | "
            f"zachowane mapy/szarości: {len(bw_report['preserved_gray_imgs'])} | "
            f"inline SVG zneutralizowane: {bw_report['svg_recolored']}"
        )
    print(f"  Strony (.page w HTML -> PDF): {report['expected_pages']} -> {report['rendered_pages']}")
    for p in report["pages"]:
        flag = " [OVERFLOW!]" if p["overflow_count"] > 0 else ""
        print(
            f"    str. {p['pdf_page']:02d} (data-page={p['data_pages']}) | "
            f"{p['page_size_mm'][0]}×{p['page_size_mm'][1]} mm | wypełnienie: {p['vertical_fill_pct']}%{flag}"
        )

    if report["issues"]:
        print("\nWYKRYTE PROBLEMY UKŁADU:", file=sys.stderr)
        for iss in report["issues"]:
            print(f"  ! {iss}", file=sys.stderr)

    if args.preview_dir:
        labels = [n for n in file_nums if n is not None] if (from_modular_dir and len(file_nums) == len(document.pages)) else None
        pl_items, max_prev_b = render_pdf_to_previews(
            out_pdf,
            Path(args.preview_dir).resolve(),
            args.dpi,
            max_side=args.max_side,
            quality=args.quality,
            page_labels=labels,
        )
        print(
            f"Wyrenderowano {len(pl_items)} podglądów RGB JPEG do: {args.preview_dir} "
            f"(maks. plik: {max_prev_b / 1024:.1f} KB, limit < 1 MB)"
        )
        if args.compare_dir and args.diff_dir:
            diff_count, max_diff_b = build_side_by_side_diffs(
                Path(args.compare_dir).resolve(),
                pl_items,
                Path(args.diff_dir).resolve(),
                page_meta=page_meta,
                page_offset=args.page_offset,
                from_modular_dir=from_modular_dir,
                max_side=args.max_side,
                quality=args.quality,
            )
            print(
                f"Zapisano {diff_count} porównań 1:1 RGB JPEG do: {args.diff_dir} "
                f"(maks. plik: {max_diff_b / 1024:.1f} KB, limit < 1 MB)"
            )

    if args.strict and not report["ok"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
