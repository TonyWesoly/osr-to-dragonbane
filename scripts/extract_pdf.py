#!/usr/bin/env python3
"""Ekstrakcja modułów OSR z PDF: metryki w mm, lekkie podglądy RGB JPEG do Visual QA
(max 1600 px na dłuższym boku, jakość ~82%, twardy limit < 1 MB), stylizowany tekst,
obrazy rastrowe oraz wycinanie map wektorowych przez bbox w 300–600 DPI (wyłącznie do PDF).

Użycie:
  1. Pełna ekstrakcja modułu:
     .venv/bin/python scripts/extract_pdf.py extract modules/<slug>/input/plik.pdf modules/<slug>/work/
  2. Wycięcie regionu wektorowego (np. mapy) przez bbox (pełne 300–600 DPI do osadzenia w PDF):
     .venv/bin/python scripts/extract_pdf.py crop modules/<slug>/input/plik.pdf --page 2 --bbox 10,15,130,195 --unit mm --dpi 450 -o modules/<slug>/work/maps/map_p02.png
  3. Konwersja istniejących podglądów PNG na lekkie RGB JPEG (< 1 MB, max 1600 px):
     .venv/bin/python scripts/extract_pdf.py convert-previews modules/<slug>/work/pages_png modules/<slug>/work/pages_jpg
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
from collections import Counter
from pathlib import Path

import pymupdf as fitz  # PyMuPDF
from PIL import Image

PT_TO_MM = 25.4 / 72.0
MM_TO_PT = 72.0 / 25.4

# Twarde limity podglądów Visual QA (ochrona przed HTTP 400 INVALID_MEDIA)
DEFAULT_PREVIEW_DPI = 150
DEFAULT_PREVIEW_MAX_SIDE = 1600
DEFAULT_PREVIEW_QUALITY = 82
HARD_MAX_PREVIEW_BYTES = 980_000  # bezpiecznie poniżej 1 MB (1 000 000 B)


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
    """Zapisuje lekki podgląd RGB JPEG do Visual QA:
    - maksymalnie `max_side` px na dłuższym boku (domyślnie 1600 px),
    - domyślna jakość ~82%,
    - twardy limit rozmiaru < 1 MB (automatyczna redukcja jakości / rozmiaru w razie potrzeby).
    """
    out_path = out_path.with_suffix(".jpg")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    work = to_rgb_image(im)
    w, h = work.size
    longest = max(w, h)
    if longest > max_side:
        scale = max_side / float(longest)
        work = work.resize((max(1, int(round(w * scale))), max(1, int(round(h * scale)))), Image.Resampling.LANCZOS)

    # Próba zapisu z docelową jakością; w razie przekroczenia limitu stopniowe obniżanie jakości/skali
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
        # Jeśli mimo quality=50 plik nadal jest za duży, zmniejsz rozdzielczość o 15%
        nw = max(400, int(round(cur_im.width * 0.85)))
        nh = max(400, int(round(cur_im.height * 0.85)))
        cur_im = cur_im.resize((nw, nh), Image.Resampling.LANCZOS)

    # Ostatnia linia obrony (zawsze < max_bytes)
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


def pt_to_mm(val: float) -> float:
    return round(val * PT_TO_MM, 2)


def classify_format(w_mm: float, h_mm: float) -> dict:
    """Klasyfikuje format strony oryginału i sugeruje format europejski."""
    w, h = sorted([w_mm, h_mm])
    if w <= 155 and h <= 225:
        orig_guess = (
            "US Digest (~140×216 mm)"
            if (135 <= w <= 145 and 212 <= h <= 220)
            else "A5 (~148×210 mm)"
            if (144 <= w <= 152 and 206 <= h <= 214)
            else f"Zbliżony do A5 ({w_mm}×{h_mm} mm)"
        )
        target = "A5 (148×210 mm) — booklet 2-up na A4 poziomo"
    else:
        orig_guess = (
            "US Letter (~216×279 mm)"
            if (212 <= w <= 220 and 275 <= h <= 284)
            else "A4 (~210×297 mm)"
            if (206 <= w <= 214 and 293 <= h <= 301)
            else f"Duży format ({w_mm}×{h_mm} mm)"
        )
        target = "A4 (210×297 mm) — booklet 2-up na A3 poziomo lub druk domowy A4 1:1"
    return {
        "detected_original_format": orig_guess,
        "recommended_eu_target": target,
    }


def span_flags(flags: int, font_name: str) -> tuple[bool, bool, bool]:
    """Zwraca (is_bold, is_italic, is_mono) z flag PyMuPDF i nazwy fontu."""
    fname = font_name.lower()
    is_bold = bool(flags & 16) or any(k in fname for k in ("bold", "black", "heavy", "demi", "semibold", "medi"))
    is_italic = bool(flags & 2) or any(k in fname for k in ("italic", "oblique", "slant"))
    is_mono = bool(flags & 8) or any(k in fname for k in ("mono", "courier", "consolas", "code"))
    return is_bold, is_italic, is_mono


def format_md_span(text: str, bold: bool, italic: bool) -> str:
    if not text or not text.strip():
        return text
    lead = len(text) - len(text.lstrip(" "))
    trail = len(text) - len(text.rstrip(" "))
    core = text.strip(" ")
    if bold and italic:
        wrapped = f"***{core}***"
    elif bold:
        wrapped = f"**{core}**"
    elif italic:
        wrapped = f"*{core}*"
    else:
        wrapped = core
    return (" " * lead) + wrapped + (" " * trail)


def merge_adjacent_spans(spans: list[dict]) -> list[dict]:
    merged: list[dict] = []
    for sp in spans:
        txt = sp["text"]
        if not txt:
            continue
        if (
            merged
            and merged[-1]["bold"] == sp["bold"]
            and merged[-1]["italic"] == sp["italic"]
            and abs(merged[-1]["size"] - sp["size"]) < 0.4
            and merged[-1]["color"] == sp["color"]
        ):
            merged[-1]["text"] += txt
        else:
            merged.append(dict(sp))
    return merged


def detect_alignment(lines: list[dict], block_x0: float, block_x1: float) -> str:
    """Heurystycznie określa wyrównanie akapitu (left, right, center, justify)."""
    if len(lines) < 2:
        return "left"
    body_lines = lines[:-1]
    widths = [ln["bbox"][2] - ln["bbox"][0] for ln in body_lines]
    block_w = max(block_x1 - block_x0, 1.0)
    left_deltas = [abs(ln["bbox"][0] - block_x0) for ln in body_lines]
    right_deltas = [abs(ln["bbox"][2] - block_x1) for ln in body_lines]
    centers = [(ln["bbox"][0] + ln["bbox"][2]) / 2.0 for ln in lines]
    block_center = (block_x0 + block_x1) / 2.0

    if all(abs(c - block_center) < 3.0 for c in centers) and max(left_deltas, default=0) > 3.0:
        return "center"
    if len(body_lines) >= 2 and all(r < 2.5 for r in right_deltas) and all(w > block_w * 0.78 for w in widths):
        return "justify"
    if all(r < 2.5 for r in right_deltas) and any(l > 6.0 for l in left_deltas):
        return "right"
    return "left"


def extract_page_text_structured(page: fitz.Page) -> tuple[dict, str]:
    """Ekstrahuje ustrukturyzowany tekst i Markdown z zachowaniem stylów, wcięć i wyrównania."""
    page_dict = page.get_text("dict", flags=fitz.TEXTFLAGS_TEXT)
    page_w = page.rect.width
    page_h = page.rect.height

    blocks_out = []
    md_lines: list[str] = []
    font_counter: Counter[tuple[str, float]] = Counter()

    text_blocks = [b for b in page_dict.get("blocks", []) if b.get("type") == 0]
    mid_x = page_w / 2.0
    left_col = [b for b in text_blocks if b["bbox"][2] <= mid_x + 12.0]
    right_col = [b for b in text_blocks if b["bbox"][0] >= mid_x - 12.0]
    is_two_col = len(left_col) >= 2 and len(right_col) >= 2

    if is_two_col:
        def sort_key(b):
            x0, y0, x1, y1 = b["bbox"]
            is_full = (x1 - x0) > page_w * 0.58
            if is_full and y0 < page_h * 0.25:
                return (0, y0, x0)
            if is_full and y0 >= page_h * 0.75:
                return (3, y0, x0)
            if x1 <= mid_x + 12.0:
                return (1, y0, x0)
            if x0 >= mid_x - 12.0:
                return (2, y0, x0)
            return (1.5, y0, x0)
        text_blocks.sort(key=sort_key)
    else:
        text_blocks.sort(key=lambda b: (round(b["bbox"][1], 1), round(b["bbox"][0], 1)))

    for b_idx, block in enumerate(text_blocks):
        bx0, by0, bx1, by1 = block["bbox"]
        lines_data = []
        block_md_lines = []

        for line in block.get("lines", []):
            raw_spans = []
            for sp in line.get("spans", []):
                txt = sp.get("text", "")
                if not txt:
                    continue
                size = round(float(sp.get("size", 0.0)), 1)
                font = sp.get("font", "")
                is_b, is_i, is_m = span_flags(int(sp.get("flags", 0)), font)
                color_int = int(sp.get("color", 0))
                color_hex = f"#{color_int:06x}"
                font_counter[(font, size)] += len(txt.strip())
                raw_spans.append(
                    {
                        "text": txt,
                        "font": font,
                        "size": size,
                        "bold": is_b,
                        "italic": is_i,
                        "mono": is_m,
                        "color": color_hex,
                    }
                )
            if not raw_spans:
                continue
            merged = merge_adjacent_spans(raw_spans)
            line_md = "".join(format_md_span(s["text"], s["bold"], s["italic"]) for s in merged).rstrip()
            lx0, ly0, lx1, ly1 = line["bbox"]
            lines_data.append(
                {
                    "bbox": [round(lx0, 2), round(ly0, 2), round(lx1, 2), round(ly1, 2)],
                    "indent_mm": pt_to_mm(lx0 - bx0),
                    "x0_mm": pt_to_mm(lx0),
                    "spans": merged,
                    "markdown": line_md,
                }
            )
            block_md_lines.append(line_md)

        if not lines_data:
            continue

        align = detect_alignment(lines_data, bx0, bx1)
        sizes = [s["size"] for ln in lines_data for s in ln["spans"] if s["text"].strip()]
        dominant_size = max(sizes) if sizes else 0.0
        col_hint = (
            "left"
            if is_two_col and bx1 <= mid_x + 12.0
            else "right"
            if is_two_col and bx0 >= mid_x - 12.0
            else "full"
        )

        blocks_out.append(
            {
                "block_index": b_idx,
                "bbox_pt": [round(bx0, 2), round(by0, 2), round(bx1, 2), round(by1, 2)],
                "bbox_mm": [pt_to_mm(bx0), pt_to_mm(by0), pt_to_mm(bx1), pt_to_mm(by1)],
                "column": col_hint,
                "align": align,
                "max_size_pt": dominant_size,
                "lines": lines_data,
            }
        )

        meta_tag = f"<!-- blk {b_idx} | col:{col_hint} | align:{align} | x:{pt_to_mm(bx0)}mm y:{pt_to_mm(by0)}mm | max:{dominant_size}pt -->"
        md_lines.append(meta_tag)
        md_lines.append("\n".join(block_md_lines))
        md_lines.append("")

    page_struct = {
        "page_number": page.number + 1,
        "width_pt": round(page_w, 2),
        "height_pt": round(page_h, 2),
        "width_mm": pt_to_mm(page_w),
        "height_mm": pt_to_mm(page_h),
        "layout_guess": "two-column" if is_two_col else "single-column",
        "drawing_count": len(page.get_drawings()),
        "blocks": blocks_out,
        "top_fonts": [
            {"font": f, "size_pt": s, "chars": c}
            for (f, s), c in font_counter.most_common(12)
        ],
    }
    return page_struct, "\n".join(md_lines).strip()


def cmd_extract(args: argparse.Namespace) -> int:
    pdf_path = Path(args.pdf).resolve()
    out_dir = Path(args.out_dir).resolve()
    pages_jpg_dir = out_dir / "pages_jpg"
    images_dir = out_dir / "images"
    if not args.skip_preview:
        pages_jpg_dir.mkdir(parents=True, exist_ok=True)
    images_dir.mkdir(parents=True, exist_ok=True)

    doc = fitz.open(pdf_path)
    num_pages = len(doc)

    all_pages_struct = []
    all_md_parts = [f"# Ekstrakcja tekstowa: {pdf_path.name}\n"]
    global_fonts: Counter[tuple[str, float]] = Counter()
    extracted_images = []
    seen_xref_hash: dict[str, str] = {}
    page_sizes: Counter[tuple[float, float]] = Counter()

    zoom = args.dpi / 72.0
    mat = fitz.Matrix(zoom, zoom)
    max_preview_bytes = 0

    for idx in range(num_pages):
        page = doc[idx]
        pno = idx + 1
        w_mm = pt_to_mm(page.rect.width)
        h_mm = pt_to_mm(page.rect.height)
        page_sizes[(w_mm, h_mm)] += 1

        # 1. Lekki podgląd RGB JPEG do Visual QA (max 1600 px, jakość ~82%, < 1 MB)
        if not args.skip_preview:
            pix = page.get_pixmap(matrix=mat, alpha=False)
            im = pixmap_to_pil_rgb(pix)
            jpg_path = pages_jpg_dir / f"page_{pno:02d}.jpg"
            _, nbytes, _ = save_preview_jpeg(
                im,
                jpg_path,
                max_side=args.max_side,
                quality=args.quality,
            )
            max_preview_bytes = max(max_preview_bytes, nbytes)

        # 2. Tekst z zachowaniem stylów
        p_struct, p_md = extract_page_text_structured(page)
        for tf in p_struct["top_fonts"]:
            global_fonts[(tf["font"], tf["size_pt"])] += tf["chars"]

        # 3. Obrazy rastrowe na stronie (pełna jakość wyłącznie do osadzania w PDF!)
        page_img_refs = []
        img_list = page.get_images(full=True)
        for img_idx, img_info in enumerate(img_list, 1):
            xref = img_info[0]
            smask = img_info[1]
            try:
                base = doc.extract_image(xref)
            except Exception:
                continue
            img_bytes = base["image"]
            ext = base.get("ext", "png")
            width = base.get("width", 0)
            height = base.get("height", 0)
            digest = hashlib.sha1(img_bytes).hexdigest()[:12]

            rects = page.get_image_rects(xref)
            rects_mm = [
                [pt_to_mm(r.x0), pt_to_mm(r.y0), pt_to_mm(r.x1), pt_to_mm(r.y1)]
                for r in rects
            ]

            if digest in seen_xref_hash:
                filename = seen_xref_hash[digest]
            else:
                if smask > 0:
                    try:
                        pix_rgb = fitz.Pixmap(doc, xref)
                        pix_mask = fitz.Pixmap(doc, smask)
                        if pix_rgb.n - pix_rgb.alpha > 3:
                            pix_rgb = fitz.Pixmap(fitz.csRGB, pix_rgb)
                        pix_rgba = fitz.Pixmap(pix_rgb, pix_mask)
                        filename = f"p{pno:02d}_img{img_idx:02d}_xref{xref}.png"
                        pix_rgba.save(images_dir / filename)
                        ext = "png"
                    except Exception:
                        filename = f"p{pno:02d}_img{img_idx:02d}_xref{xref}.{ext}"
                        (images_dir / filename).write_bytes(img_bytes)
                else:
                    filename = f"p{pno:02d}_img{img_idx:02d}_xref{xref}.{ext}"
                    (images_dir / filename).write_bytes(img_bytes)
                seen_xref_hash[digest] = filename

            rec = {
                "page": pno,
                "file": f"images/{filename}",
                "xref": xref,
                "smask": smask,
                "width_px": width,
                "height_px": height,
                "ext": ext,
                "sha1_12": digest,
                "rects_mm": rects_mm,
            }
            page_img_refs.append(rec)
            extracted_images.append(rec)

        p_struct["images"] = page_img_refs
        all_pages_struct.append(p_struct)

        side = "prawa/nieparzysta" if pno % 2 == 1 else "lewa/parzysta"
        all_md_parts.append(
            f"\n---\n## STRONA {pno} ({side} | {w_mm}×{h_mm} mm | {p_struct['layout_guess']} | rysunki wekt.: {p_struct['drawing_count']} | obrazy: {len(page_img_refs)})\n"
        )
        all_md_parts.append(p_md)

    most_common_size = page_sizes.most_common(1)[0][0]
    fmt_info = classify_format(most_common_size[0], most_common_size[1])

    vector_heavy_pages = [
        {"page": p["page_number"], "drawing_count": p["drawing_count"], "image_count": len(p["images"])}
        for p in all_pages_struct
        if p["drawing_count"] >= 50
    ]

    metadata = {
        "source_pdf": str(pdf_path),
        "page_count": num_pages,
        "is_multiple_of_4": (num_pages % 4 == 0),
        "dominant_page_size_mm": {"width_mm": most_common_size[0], "height_mm": most_common_size[1]},
        "all_page_sizes_mm": [
            {"width_mm": k[0], "height_mm": k[1], "count": v} for k, v in page_sizes.items()
        ],
        **fmt_info,
        "preview_format": "jpeg",
        "preview_dir": "pages_jpg",
        "preview_dpi": args.dpi,
        "preview_max_side_px": args.max_side,
        "preview_quality": args.quality,
        "unique_raster_images": len(seen_xref_hash),
        "total_image_placements": len(extracted_images),
        "vector_heavy_pages": vector_heavy_pages,
        "dominant_fonts": [
            {"font": f, "size_pt": s, "chars": c}
            for (f, s), c in global_fonts.most_common(25)
        ],
        "toc": doc.get_toc(),
        "pdf_metadata": doc.metadata,
    }

    (out_dir / "metrics.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "text_structured.json").write_text(
        json.dumps({"metadata": metadata, "pages": all_pages_struct}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (out_dir / "text_styled.md").write_text("\n".join(all_md_parts), encoding="utf-8")

    print(f"Wyekstrahowano: {pdf_path.name}")
    print(f"  Strony: {num_pages} (wielokrotność 4: {metadata['is_multiple_of_4']})")
    print(f"  Wymiary dominujące: {most_common_size[0]}×{most_common_size[1]} mm -> {fmt_info['detected_original_format']}")
    print(f"  Rekomendacja EU: {fmt_info['recommended_eu_target']}")
    if not args.skip_preview:
        print(f"  Podglądy Visual QA (RGB JPEG -> pages_jpg/): max {max_preview_bytes / 1024:.1f} KB (limit < 1 MB)")
    print(f"  Obrazy rastrowe (unikalne/wystąpienia): {len(seen_xref_hash)}/{len(extracted_images)}")
    print(f"  Strony bogate wektorowo (>=50 ścieżek): {[v['page'] for v in vector_heavy_pages]}")
    print(f"  Zapisano do: {out_dir}")
    return 0


def cmd_crop(args: argparse.Namespace) -> int:
    """Wycina obszar strony PDF przez bbox (idealne do map wektorowych / logo) w 300–600 DPI.
    Plik wynikowy służy wyłącznie do osadzania w finalnym PDF — nie otwieraj go bezpośrednio w Visual QA!"""
    pdf_path = Path(args.pdf).resolve()
    out_path = Path(args.output).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    doc = fitz.open(pdf_path)
    if args.page < 1 or args.page > len(doc):
        raise ValueError(f"Numer strony {args.page} poza zakresem 1..{len(doc)}")
    page = doc[args.page - 1]

    if args.bbox:
        coords = [float(x.strip()) for x in args.bbox.split(",")]
        if len(coords) != 4:
            raise ValueError("Parametr --bbox wymaga 4 wartości: x0,y0,x1,y1")
        x0, y0, x1, y1 = coords
        if args.unit == "mm":
            rect = fitz.Rect(x0 * MM_TO_PT, y0 * MM_TO_PT, x1 * MM_TO_PT, y1 * MM_TO_PT)
        elif args.unit == "frac":
            pw, ph = page.rect.width, page.rect.height
            rect = fitz.Rect(x0 * pw, y0 * ph, x1 * pw, y1 * ph)
        else:
            rect = fitz.Rect(x0, y0, x1, y1)
    else:
        rect = page.rect

    if args.strip_text:
        for blk in page.get_text("dict").get("blocks", []):
            if blk.get("type") != 0:
                continue
            brect = fitz.Rect(blk["bbox"])
            if brect.intersects(rect):
                page.add_redact_annot(brect, fill=False)
        page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE, graphics=fitz.PDF_REDACT_LINE_ART_NONE)

    zoom = args.dpi / 72.0
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat, clip=rect, alpha=args.transparent)
    pix.save(out_path)
    print(
        f"Wycięto str. {args.page} [{pt_to_mm(rect.x0)}, {pt_to_mm(rect.y0)}, {pt_to_mm(rect.x1)}, {pt_to_mm(rect.y1)} mm] "
        f"@ {args.dpi} DPI -> {out_path} ({pix.width}×{pix.height} px, {out_path.stat().st_size / 1024:.1f} KB)"
    )
    return 0


def cmd_convert_previews(args: argparse.Namespace) -> int:
    """Konwertuje istniejący katalog podglądów (np. ciężkich PNG) na lekkie RGB JPEG (< 1 MB, max 1600 px)."""
    src_dir = Path(args.src_dir).resolve()
    dst_dir = Path(args.dst_dir).resolve()
    dst_dir.mkdir(parents=True, exist_ok=True)

    exts = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tif", ".tiff"}
    files = sorted(p for p in src_dir.iterdir() if p.is_file() and p.suffix.lower() in exts)
    if not files:
        print(f"Brak obrazów do konwersji w: {src_dir}")
        return 0

    max_bytes = 0
    total_bytes = 0
    for src_p in files:
        with Image.open(src_p) as im:
            out_p, nbytes, size = save_preview_jpeg(
                im,
                dst_dir / src_p.name,
                max_side=args.max_side,
                quality=args.quality,
            )
        max_bytes = max(max_bytes, nbytes)
        total_bytes += nbytes
        if args.delete_src and src_p.resolve() != out_p.resolve():
            src_p.unlink()

    print(
        f"Przekonwertowano {len(files)} podglądów -> {dst_dir} "
        f"(łącznie {total_bytes / 1024:.1f} KB, maks. plik: {max_bytes / 1024:.1f} KB, limit < 1 MB)"
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Ekstrakcja zasobów, metryk, tekstu, lekkich podglądów RGB JPEG i map wektorowych z PDF."
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    p_ext = sub.add_parser("extract", help="Pełna ekstrakcja modułu do katalogu roboczego.")
    p_ext.add_argument("pdf", help="Ścieżka do pliku PDF.")
    p_ext.add_argument("out_dir", help="Katalog wyjściowy (np. modules/<slug>/work).")
    p_ext.add_argument("--dpi", type=int, default=DEFAULT_PREVIEW_DPI, help=f"DPI rasteryzacji podglądów (domyślnie {DEFAULT_PREVIEW_DPI}).")
    p_ext.add_argument("--max-side", type=int, default=DEFAULT_PREVIEW_MAX_SIDE, help=f"Maks. dłuższy bok podglądu JPEG w px (domyślnie {DEFAULT_PREVIEW_MAX_SIDE}).")
    p_ext.add_argument("--quality", type=int, default=DEFAULT_PREVIEW_QUALITY, help=f"Jakość JPEG 1–95 (domyślnie {DEFAULT_PREVIEW_QUALITY}).")
    p_ext.add_argument("--skip-preview", "--skip-png", dest="skip_preview", action="store_true", help="Pomiń generowanie podglądów stron.")
    p_ext.set_defaults(func=cmd_extract)

    p_crop = sub.add_parser("crop", help="Wytnij region strony PDF (np. mapę wektorową) w 300–600 DPI do osadzenia w PDF.")
    p_crop.add_argument("pdf", help="Ścieżka do pliku PDF.")
    p_crop.add_argument("--page", type=int, required=True, help="Numer strony (1-based).")
    p_crop.add_argument("--bbox", help="Współrzędne x0,y0,x1,y1 (domyślnie cała strona).")
    p_crop.add_argument("--unit", choices=["mm", "pt", "frac"], default="mm", help="Jednostka bbox: mm (domyślnie), pt lub frac (0.0–1.0).")
    p_crop.add_argument("--dpi", type=int, default=450, help="Rozdzielczość wyjścia w DPI (domyślnie 450).")
    p_crop.add_argument("--transparent", action="store_true", help="Zachowaj kanał alfa (przezroczyste tło).")
    p_crop.add_argument("--strip-text", action="store_true", help="Usuń wektorowy tekst PDF w wycinanym obszarze.")
    p_crop.add_argument("-o", "--output", required=True, help="Plik wynikowy PNG (do osadzenia w PDF).")
    p_crop.set_defaults(func=cmd_crop)

    p_conv = sub.add_parser("convert-previews", help="Konwertuj katalog podglądów (np. PNG) na lekkie RGB JPEG (< 1 MB, max 1600 px).")
    p_conv.add_argument("src_dir", help="Katalog źródłowy z obrazami.")
    p_conv.add_argument("dst_dir", help="Katalog docelowy na lekkie RGB JPEG.")
    p_conv.add_argument("--max-side", type=int, default=DEFAULT_PREVIEW_MAX_SIDE, help=f"Maks. dłuższy bok w px (domyślnie {DEFAULT_PREVIEW_MAX_SIDE}).")
    p_conv.add_argument("--quality", type=int, default=DEFAULT_PREVIEW_QUALITY, help=f"Jakość JPEG (domyślnie {DEFAULT_PREVIEW_QUALITY}).")
    p_conv.add_argument("--delete-src", action="store_true", help="Usuń oryginalne pliki po udanej konwersji.")
    p_conv.set_defaults(func=cmd_convert_previews)

    return p


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
