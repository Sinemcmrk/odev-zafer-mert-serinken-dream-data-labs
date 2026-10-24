"""API ve .env gerektirmeyen görsel regresyon kontrolleri.

Çalıştırma: python -B -m unittest discover -s tests -v
"""

import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from PIL import Image, ImageChops, ImageDraw

import image_generator as generator


ROOT = Path(__file__).resolve().parents[1]
BRANDS = ("aba_psikoloji", "aba_egitim", "e4i", "design_house_global")


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


class OfflineImageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="ddl-layout-test-")
        self.addCleanup(self.temp.cleanup)
        self.output = Path(self.temp.name)
        self.kits = {brand: read_json(ROOT / "brand_kits" / f"{brand}.json") for brand in BRANDS}
        self.examples = {brand: read_json(ROOT / "examples" / f"{brand}.json") for brand in BRANDS}

    def render_checked(self, brand, post, name, **kwargs):
        """Gerçekte çizilen mürekkep sınırlarını ve ayrı alanların çakışmasını ölçer."""
        text_regions, media_regions, ink_boxes = [], [], []
        text_box = generator.draw_text_box
        media = generator.draw_brand_media
        text = ImageDraw.ImageDraw.text

        def tracked_box(draw, value, box, *args, **options):
            text_regions.append(box)
            before = len(ink_boxes)
            result = text_box(draw, value, box, *args, **options)
            self.assertEqual("".join(str(value).split()), "".join("".join(result[1]).split()))
            for ink in ink_boxes[before:]:
                self.assertGreaterEqual(ink[0], box[0])
                self.assertGreaterEqual(ink[1], box[1])
                self.assertLessEqual(ink[2], box[2])
                self.assertLessEqual(ink[3], box[3])
            return result

        def tracked_media(image, brand_id, box, *args, **options):
            media_regions.append(box)
            return media(image, brand_id, box, *args, **options)

        def tracked_text(draw, xy, value, *args, **options):
            ink = draw.textbbox(xy, value, font=options["font"], anchor=options.get("anchor"))
            self.assertTrue(0 <= ink[0] <= ink[2] <= 1080)
            self.assertTrue(0 <= ink[1] <= ink[3] <= 1080)
            ink_boxes.append(ink)
            return text(draw, xy, value, *args, **options)

        before = json.dumps((self.kits[brand], post), ensure_ascii=False)
        with patch.object(generator, "draw_text_box", tracked_box), \
             patch.object(generator, "draw_brand_media", tracked_media), \
             patch.object(ImageDraw.ImageDraw, "text", tracked_text):
            path = generator.create_post_image(self.kits[brand], post, str(self.output / name), **kwargs)
        self.assertEqual(before, json.dumps((self.kits[brand], post), ensure_ascii=False))
        regions = text_regions + media_regions + [(900, 56, 1008, 164)]
        for index, first in enumerate(regions):
            for second in regions[index + 1:]:
                self.assertTrue(first[2] <= second[0] or second[2] <= first[0]
                                or first[3] <= second[1] or second[3] <= first[1],
                                f"Çakışan alanlar: {first}, {second}")
        with Image.open(path) as output:
            output.load()
            self.assertEqual(output.size, (1080, 1080))
            self.assertEqual(output.mode, "RGB")
            self.assertEqual(output.format, "PNG")
            # Kaynak logonun renkleri/oranı korunmalı, üzeri metinle örtülmemeli.
            expected = Image.new("RGB", (108, 108), self.kits[brand]["colors"]["background"])
            with Image.open(ROOT / self.kits[brand]["logo"]) as logo_file:
                logo = logo_file.convert("RGBA")
                logo.thumbnail((108, 108), Image.Resampling.LANCZOS)
            expected.paste(logo, ((108 - logo.width) // 2, (108 - logo.height) // 2), logo)
            self.assertIsNone(ImageChops.difference(output.crop((900, 56, 1008, 164)), expected).getbbox())
        return path

    def test_examples_and_reference_posts_fit_without_clipping(self):
        posts = list(self.examples.values()) + read_json(ROOT / "post_library" / "posts.json")
        for index, post in enumerate(posts):
            with self.subTest(brand=post["brand_id"], index=index):
                self.render_checked(post["brand_id"], post, f"post-{index}.png")

    def test_local_photo_and_missing_photo_fallback(self):
        # Test görseli yerel olarak üretilir; dışarıdan görsel indirilmez.
        photo = self.output / "fixture.png"
        fixture = Image.new("RGB", (240, 360), "#E3CAB1")
        ImageDraw.Draw(fixture).rectangle((0, 0, 120, 360), fill="#467177")
        fixture.save(photo)
        for brand in BRANDS:
            with self.subTest(brand=brand):
                original = self.render_checked(brand, self.examples[brand], f"{brand}-plain.png")
                with_photo = self.render_checked(brand, self.examples[brand], f"{brand}-photo.png", photo_path=photo)
                missing = self.render_checked(brand, self.examples[brand], f"{brand}-missing.png", photo_path=self.output / "missing.jpg")
                self.assertNotEqual(original.read_bytes(), with_photo.read_bytes())
                self.assertEqual(original.read_bytes(), missing.read_bytes())

    def test_invalid_photo_has_clear_error_and_does_not_overwrite(self):
        destination = self.output / "existing.png"
        destination.write_bytes(b"existing output")
        bad = self.output / "broken.jpg"
        bad.write_bytes(b"not an image")
        with self.assertRaisesRegex(ValueError, "okunamadı"):
            generator.create_post_image(self.kits["e4i"], self.examples["e4i"], str(destination), photo_path=bad)
        self.assertEqual(destination.read_bytes(), b"existing output")
        with self.assertRaisesRegex(ValueError, "yerel görsel"):
            generator.create_post_image(self.kits["e4i"], self.examples["e4i"], str(destination), photo_path=".env")

    def test_long_word_keeps_all_characters_and_extreme_text_fails_cleanly(self):
        post = dict(self.examples["aba_egitim"], body="Üniversite" * 12)
        self.render_checked("aba_egitim", post, "long-word.png")
        destination = self.output / "too-long.png"
        with self.assertRaisesRegex(ValueError, "sığmıyor"):
            generator.create_post_image(self.kits["aba_egitim"], dict(post, body="uzun metin " * 1000), str(destination))
        self.assertFalse(destination.exists())

    def test_sized_fallback_when_system_fonts_are_unavailable(self):
        generator.get_font.cache_clear()
        try:
            with patch.object(Path, "is_file", return_value=False):
                small = generator.get_font(18, True, "condensed")
                large = generator.get_font(48, True, "condensed")
                self.assertGreater(large.getlength("Design notes"), small.getlength("Design notes"))
        finally:
            generator.get_font.cache_clear()


if __name__ == "__main__":
    unittest.main()
