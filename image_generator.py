
from functools import lru_cache
from pathlib import Path
import re

from PIL import Image, ImageDraw, ImageFont, ImageOps, UnidentifiedImageError


BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "generated_posts"
OUTPUT_DIR.mkdir(exist_ok=True)


@lru_cache(maxsize=256)
def get_font(size, bold=False, style="sans"):
    """Kurulu fontları kullanır; font dosyası indirmez veya dağıtmaz.

    Brand Kit'teki Montserrat/Oswald yönelimlerine görsel alternatiflerdir;
    resmî marka fontları oldukları iddia edilmez.
    """
    preferred = {
        "warm": ["Arial Rounded Bold.ttf"],
        "heavy": ["Arial Black.ttf"],
        "condensed": ["DIN Condensed Bold.ttf", "Arial Narrow Bold.ttf"],
    }.get(style, [])
    names = preferred + ["Arial Bold.ttf" if bold else "Arial.ttf"]
    candidates = [
        Path(directory) / name
        for name in names
        for directory in ("/System/Library/Fonts/Supplemental", "/Library/Fonts")
    ]
    linux_name = "DejaVuSansCondensed-Bold.ttf" if style == "condensed" else (
        "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    )
    candidates += [
        Path("/usr/share/fonts/truetype/dejavu") / linux_name,
        Path("C:/Windows/Fonts") / ("arialbd.ttf" if bold else "arial.ttf"),
    ]
    for path in candidates:
        if path.is_file():
            try:
                return ImageFont.truetype(str(path), size)
            except OSError:
                continue
    return ImageFont.load_default(size=size)


def wrap_text(draw, text, font, max_width):
    """Uzun tek kelimeleri de bölerek metnin tamamını korur."""
    lines = []
    for paragraph in str(text).splitlines() or [""]:
        current = ""
        for word in paragraph.split():
            candidate = f"{current} {word}".strip()
            if draw.textlength(candidate, font=font) <= max_width:
                current = candidate
                continue
            if current:
                lines.append(current)
            current = ""
            for char in word:
                if current and draw.textlength(current + char, font=font) > max_width:
                    lines.append(current)
                    current = ""
                current += char
        if current:
            lines.append(current)
    return lines


def prepare_text(
    draw, text, max_width, max_height,
    start_size, min_size, bold=False, style="sans"
):
    """Metin ayrılan alana sığana kadar fontu küçültür."""
    for size in range(start_size, min_size - 1, -1):
        font = get_font(size, bold=bold, style=style)
        lines = wrap_text(draw, text, font, max_width)

        ascent, descent = font.getmetrics()
        line_height = ascent + descent + 8
        total_height = len(lines) * line_height

        widest = max(
            (draw.textlength(line, font=font) for line in lines),
            default=0
        )

        # Glyph çıkıntıları ve vurgulanan kelimeler için yatay güvenlik payı.
        if total_height <= max_height and widest <= max_width:
            return font, lines, line_height, total_height
    raise ValueError("Metin ayrılan alana sığmıyor; lütfen daha kısa bir metin kullanın.")


def draw_lines(draw, lines, font, x, y, line_height, color):
    """Hazırlanan satırları görsele çizer."""
    for line in lines:
        draw.text((x, y), line, font=font, fill=color)
        y += line_height

    return y


def draw_design_house_decor(draw):
    """Design House Global için portfolyo temalı panel."""

    # Koyu portfolyo paneli
    draw.rounded_rectangle(
        (760, 220, 1000, 450),
        radius=16,
        fill="#292020",
        outline="#765A50",
        width=2
    )

    # Portfolyo kağıdı
    draw.rounded_rectangle(
        (785, 245, 975, 350),
        radius=6,
        fill="#E8DDD2"
    )

    # Tasarım eskizleri
    draw.rectangle(
        (805, 260, 865, 320),
        outline="#8F2724",
        width=3
    )

    draw.ellipse(
        (880, 260, 950, 330),
        outline="#8F2724",
        width=3
    )

    # Renk paleti
    draw.rectangle(
        (785, 375, 835, 410),
        fill="#8F2724"
    )

    draw.rectangle(
        (850, 375, 900, 410),
        fill="#C5A47E"
    )

    draw.rectangle(
        (915, 375, 965, 410),
        fill="#E8DDD2"
    )


def draw_aba_egitim_decor(draw):
    """ABA Eğitim için üniversite temalı illüstrasyon."""

    # Lacivert panel ve turuncu çerçeve
    draw.rounded_rectangle(
        (765, 230, 1000, 455),
        radius=18,
        fill="#102B4D",
        outline="#E15110",
        width=3
    )

    # Üniversite çatısı
    draw.polygon(
        [(790, 310), (880, 255), (970, 310)],
        fill="#E15110"
    )

    # Üniversite sütunları
    for x in [810, 850, 890, 930]:
        draw.rectangle(
            (x, 320, x + 18, 405),
            fill="#FFFFFF"
        )

    # Binanın alt basamağı
    draw.rectangle(
        (790, 410, 970, 423),
        fill="#E15110"
    )

    # Alt dekoratif çizgi
    draw.line(
        (800, 440, 960, 440),
        fill="#E15110",
        width=3
    )


def draw_e4i_decor(draw):
    """
    Education for Innovation için teknoloji ve
    inovasyon temalı bağlantı ağı çizer.
    """

    # Koyu lacivert dekor paneli
    draw.rounded_rectangle(
        (765, 230, 1000, 455),
        radius=18,
        fill="#102348",
        outline="#62B347",
        width=3
    )

    # Bağlantı noktaları
    nodes = [
        (815, 285),
        (945, 290),
        (880, 345),
        (805, 400),
        (955, 405),
    ]

    # Ağ bağlantıları
    connections = [
        (0, 2),
        (1, 2),
        (2, 3),
        (2, 4),
        (0, 1),
        (3, 4),
    ]

    for start, end in connections:
        x1, y1 = nodes[start]
        x2, y2 = nodes[end]

        draw.line(
            (x1, y1, x2, y2),
            fill="#62B347",
            width=4
        )

    # Bağlantı noktalarının dış halkaları
    for x, y in nodes:
        draw.ellipse(
            (x - 14, y - 14, x + 14, y + 14),
            fill="#62B347"
        )

        draw.ellipse(
            (x - 6, y - 6, x + 6, y + 6),
            fill="#FFFFFF"
        )

    # Merkezde inovasyon vurgusu
    draw.ellipse(
        (855, 320, 905, 370),
        outline="#FFFFFF",
        width=3
    )


def draw_aba_psikoloji_decor(draw):
    """
    ABA Psikoloji için sakinlik ve farkındalık
    temalı yaprak illüstrasyonu çizer.
    """

    # Yumuşak krem renkli dekor paneli
    draw.rounded_rectangle(
        (765, 230, 1000, 455),
        radius=30,
        fill="#F2E8D8",
        outline="#E58F1F",
        width=3
    )

    # Bitkinin ana gövdesi
    draw.line(
        (880, 410, 880, 295),
        fill="#658A69",
        width=6
    )

    # Sol yapraklar
    draw.ellipse(
        (805, 305, 875, 355),
        fill="#86A88B",
        outline="#658A69",
        width=2
    )

    draw.ellipse(
        (820, 365, 875, 405),
        fill="#A8C3A6",
        outline="#658A69",
        width=2
    )

    # Sağ yapraklar
    draw.ellipse(
        (885, 280, 955, 330),
        fill="#86A88B",
        outline="#658A69",
        width=2
    )

    draw.ellipse(
        (885, 350, 955, 395),
        fill="#A8C3A6",
        outline="#658A69",
        width=2
    )

    # Bitkinin altındaki yumuşak zemin
    draw.arc(
        (810, 390, 950, 435),
        start=0,
        end=180,
        fill="#E58F1F",
        width=4
    )

def draw_text_box(
    draw, text, box, color, start_size=32, min_size=20,
    bold=False, style="sans", highlights=None, align="left", valign="top"
):
    """Metni kırpmadan sığdırır; her çizilen kelimenin sınırını doğrular."""
    x0, y0, x1, y1 = box
    font, lines, line_height, total_height = prepare_text(
        draw, text, x1 - x0 - 8, y1 - y0,
        start_size, min_size, bold=bold, style=style
    )
    ascent, _ = font.getmetrics()
    y = y0 + ((y1 - y0 - total_height) / 2 if valign == "center" else 0)
    for line in lines:
        width = draw.textlength(line, font=font)
        x = (x0 + x1 - width) / 2 if align == "center" else x0 + 4
        baseline = y + ascent
        for match in re.finditer(r"\S+", line):
            word = match.group()
            word_x = x + draw.textlength(line[:match.start()], font=font)
            ink = draw.textbbox((word_x, baseline), word, font=font, anchor="ls")
            if ink[0] < x0 or ink[1] < y0 or ink[2] > x1 or ink[3] > y1:
                raise ValueError("Metin güvenli çizim alanına sığmıyor.")
            key = re.sub(r"[\W_]+", "", word.casefold())
            fill = (highlights or {}).get(key, color)
            if key.isdecimal():
                fill = (highlights or {}).get("number", fill)
            draw.text((word_x, baseline), word, font=font, fill=fill, anchor="ls")
        y += line_height
    return font, lines


def draw_brand_media(image, brand_id, box, primary, photo_path=None):
    """Yerel fotoğraf varsa küçük dekorla birleştirir; yoksa dekoru korur."""
    decorators = {
        "aba_psikoloji": draw_aba_psikoloji_decor,
        "aba_egitim": draw_aba_egitim_decor,
        "e4i": draw_e4i_decor,
        "design_house_global": draw_design_house_decor,
    }
    decorator = decorators.get(brand_id)
    if decorator is None:
        return
    layer = Image.new("RGBA", (1080, 1080))
    decorator(ImageDraw.Draw(layer))
    decor = layer.crop((756, 216, 1004, 460))
    x0, y0, x1, y1 = box
    photo = None
    if photo_path is not None:
        path = Path(photo_path)
        if not path.is_absolute():
            path = BASE_DIR / path
        if path.suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tif", ".tiff"}:
            raise ValueError("Fotoğraf için desteklenen bir yerel görsel dosyası seçin.")
        if path.is_file():
            try:
                with Image.open(path) as source:
                    photo = ImageOps.fit(
                        ImageOps.exif_transpose(source).convert("RGB"),
                        (x1 - x0, y1 - y0), method=Image.Resampling.LANCZOS
                    )
            except (OSError, UnidentifiedImageError) as error:
                raise ValueError("Yerel fotoğraf dosyası okunamadı.") from error
    if photo is not None:
        mask = Image.new("L", photo.size)
        ImageDraw.Draw(mask).rounded_rectangle(
            (0, 0, photo.width - 1, photo.height - 1), radius=16, fill=255
        )
        image.paste(photo, (x0, y0), mask)
        decor.thumbnail((88, 88), Image.Resampling.LANCZOS)
        image.paste(decor, (x1 - decor.width - 8, y1 - decor.height - 8), decor)
        ImageDraw.Draw(image).rounded_rectangle(box, radius=16, outline=primary, width=2)
    else:
        decor.thumbnail((x1 - x0, y1 - y0), Image.Resampling.LANCZOS)
        image.paste(decor, (x0 + (x1 - x0 - decor.width) // 2,
                           y0 + (y1 - y0 - decor.height) // 2), decor)


def create_post_image(
    brand_kit, post_data, output_filename="post_output.png", *, photo_path=None
):
    """1080x1080 PNG üretir. Mevcut üç argümanlı çağrılar değişmeden çalışır."""
    brand_id = brand_kit["brand_id"]
    colors = brand_kit["colors"]
    primary = colors.get("primary", "#000000")
    text_color = colors.get("text", "#111111")
    background = colors.get("background", "#FFFFFF")
    image = Image.new("RGB", (1080, 1080), background)
    draw = ImageDraw.Draw(image)

    # Her markanın başlık, gövde ve medya alanları ayrıdır.
    layouts = {
        "aba_psikoloji": {
            "label": "PSİKOLOJİ NOTLARI", "style": "warm", "size": 68,
            "title": (72, 230, 744, 500), "body": (104, 580, 976, 786),
            "media": (784, 278, 1008, 502),
            "highlights": {"kaygı": colors.get("accent_burgundy", primary),
                           "kaygısı": colors.get("accent_burgundy", primary),
                           "kontrol": primary, "adım": primary, "destek": primary},
        },
        "aba_egitim": {
            "label": "EĞİTİM REHBERİ", "style": "heavy", "size": 70,
            "title": (72, 208, 1008, 480), "body": (72, 566, 658, 842),
            "media": (718, 556, 1008, 846),
            "highlights": {"number": primary, "üniversite": primary,
                           "sat": primary, "ap": primary, "hedef": primary},
        },
        "e4i": {
            "label": "IDEAS FOR TOMORROW", "style": "heavy", "size": 66,
            "title": (72, 224, 708, 510), "body": (96, 594, 984, 824),
            "media": (752, 252, 1008, 508),
            "highlights": {"ai": colors.get("accent_neon_green", primary),
                           "innovation": primary, "future": primary,
                           "learn": colors.get("accent_cyan", primary),
                           "learning": colors.get("accent_cyan", primary)},
        },
        "design_house_global": {
            "label": "CREATIVE PRACTICE", "style": "condensed", "size": 92,
            "title": (72, 228, 680, 586), "body": (72, 666, 1008, 836),
            "media": (736, 248, 1008, 564),
            "highlights": {"thinking": colors.get("accent_gold", primary),
                           "work": colors.get("accent_gold", primary),
                           "creative": colors.get("accent_gold", primary)},
        },
    }
    layout = layouts.get(brand_id, {
        "label": brand_kit["brand_name"], "style": "sans", "size": 64,
        "title": (72, 220, 1008, 500), "body": (72, 580, 1008, 836),
        "media": (752, 252, 1008, 508), "highlights": {},
    })

    # Küçük konu etiketi ve markaya özgü yapısal çizgiler.
    if brand_id == "aba_psikoloji":
        draw.ellipse((-120, -180, 570, 220), fill=colors.get("beige", background))
        draw.rounded_rectangle((72, 116, 390, 158), radius=21,
                               fill=colors.get("accent_green", primary))
        label_color = "#FFFFFF"
        draw.rounded_rectangle((72, 548, 1008, 822), radius=28, fill="#F2E8D8")
    elif brand_id == "aba_egitim":
        draw.rectangle((72, 88, 78, 164), fill=primary)
        label_color = primary
        draw.line((72, 514, 1008, 514), fill=primary, width=2)
    elif brand_id == "e4i":
        purple = colors.get("accent_purple", primary)
        draw.rounded_rectangle((72, 116, 426, 158), radius=10, fill=purple)
        label_color = "#FFFFFF"
        for x, color in ((72, primary), (128, purple), (184, colors.get("accent_cyan", primary))):
            draw.rounded_rectangle((x, 550, x + 40, 557), radius=3, fill=color)
        draw.rounded_rectangle((72, 576, 1008, 846), radius=18, fill="#102348")
    elif brand_id == "design_house_global":
        label_color = colors.get("accent_gold", primary)
        draw.line((72, 186, 1008, 186), fill=primary, width=2)
        draw.line((72, 622, 192, 622), fill=label_color, width=3)
    else:
        label_color = primary
    draw_text_box(draw, layout["label"], (88, 120, 680, 156), label_color,
                  start_size=20, min_size=16, bold=True)

    # Logo: oranı, renkleri ve saydamlığı korunur; diğer alanlarla çakışmaz.
    logo_path = BASE_DIR / brand_kit["logo"]
    if logo_path.is_file():
        with Image.open(logo_path) as source:
            logo = source.convert("RGBA")
            logo.thumbnail((108, 108), Image.Resampling.LANCZOS)
        image.paste(logo, (900 + (108 - logo.width) // 2,
                           56 + (108 - logo.height) // 2), logo)

    draw_brand_media(image, brand_id, layout["media"], primary, photo_path)
    headline = post_data["headline"]
    if brand_id == "design_house_global":
        # Türkçe talep edilmişse i/ı büyük harf dönüşümünü de koru.
        headline = headline.translate(str.maketrans({"i": "İ", "ı": "I"})).upper() if any(
            char in headline for char in "çğıöşüÇĞİÖŞÜ"
        ) else headline.upper()
    draw_text_box(draw, headline, layout["title"], text_color,
                  start_size=layout["size"], min_size=28, bold=True,
                  style=layout["style"], highlights=layout["highlights"])
    draw_text_box(draw, post_data["body"], layout["body"], text_color,
                  start_size=32 if brand_id != "design_house_global" else 30,
                  min_size=22, valign="center")

    # CTA en fazla 80 px yükseklik kaplar; başlık ve gövdenin önüne geçmez.
    cta_color = text_color
    if brand_id == "aba_psikoloji":
        draw.rounded_rectangle((72, 902, 1008, 982), radius=18,
                               fill=colors.get("beige", background))
    elif brand_id == "e4i":
        draw.rounded_rectangle((72, 902, 1008, 982), radius=12, outline=primary, width=2)
    else:
        draw.line((72, 888, 1008, 888), fill=primary, width=2)
        if brand_id == "design_house_global":
            cta_color = colors.get("accent_gold", text_color)
    draw_text_box(draw, post_data["cta"], (92, 910, 988, 974), cta_color,
                  start_size=24, min_size=18, bold=True, valign="center")
    draw_text_box(draw, brand_kit.get("website", ""), (72, 1020, 1008, 1052),
                  text_color, start_size=18, min_size=14, align="center")
    draw.rectangle((0, 1064, 1080, 1080), fill=primary)

    output_path = OUTPUT_DIR / output_filename
    image.save(output_path, "PNG")
    return output_path
