import unittest
import os

HERE = os.path.dirname(__file__)


class scale_image_test(unittest.TestCase):
    def scale_image(self, *a, **kw):
        from s4u.image.scale import scale_image
        return scale_image(*a, **kw)

    def test_return_value(self):
        from StringIO import StringIO
        from s4u.image.testing import PNG
        result = self.scale_image(StringIO(PNG), width=10)
        self.assertEqual(result[1], 'PNG')
        self.assertEqual(result[2], (10, 10))

    def test_gif_converted_to_png(self):
        from StringIO import StringIO
        from s4u.image.testing import GIF
        self.assertEqual(
            self.scale_image(StringIO(GIF), width=10)[1], 'PNG')

    def test_jpeg_stays_jpeg(self):
        from StringIO import StringIO
        from s4u.image.testing import JPEG
        self.assertEqual(
            self.scale_image(StringIO(JPEG), width=10)[1], 'JPEG')

    def test_bad1(self):
        image = open(os.path.join(HERE, 'bad1.jpg'), 'rb')
        (image, format, size) = self.scale_image(image, 200, 200, True, True)

    def test_bad2(self):
        image = open(os.path.join(HERE, 'bad2.jpg'), 'rb')
        (image, format, size) = self.scale_image(image, 200, 200, False, True)

    def test_bad3(self):
        image = open(os.path.join(HERE, 'bad3.jpg'), 'rb')
        (image, format, size) = self.scale_image(image, 200, 200, True, True)


class correct_colour_mode_tests(unittest.TestCase):
    def correct_colour_mode(self, *a, **kw):
        from s4u.image.scale import correct_colour_mode
        return correct_colour_mode(*a, **kw)

    def test_convert_black_white_to_greyscale(self):
        import PIL.Image
        self.assertEqual(
                self.correct_colour_mode(PIL.Image.new('1', (50, 50))).mode,
                'L')

    def test_convert_palette_to_rgba(self):
        import PIL.Image
        self.assertEqual(
                self.correct_colour_mode(PIL.Image.new('P', (50, 50))).mode,
                'RGBA')

    def test_convert_cmyk(self):
        import PIL.Image
        self.assertEqual(
                self.correct_colour_mode(PIL.Image.new('CMYK', (50, 50))).mode,
                'RGB')

    def test_rgb_image_not_touched(self):
        import PIL.Image
        image = PIL.Image.new('RGB', (50, 50))
        self.assertTrue(self.correct_colour_mode(image) is image)


class center_crop_tests(unittest.TestCase):
    def center_crop(self, *a, **kw):
        from s4u.image.scale import center_crop
        return center_crop(*a, **kw)

    def test_image_smaller_than_crop_size(self):
        import PIL.Image
        image = PIL.Image.new('L', (50, 60))
        crop = self.center_crop(image, 100, 100)
        self.assertEqual(crop.size, (50, 60))

    def test_crop_width_only(self):
        import PIL.Image
        image = PIL.Image.new('L', (50, 60))
        crop = self.center_crop(image, 30, 100)
        self.assertEqual(crop.size, (30, 60))

    def test_crop_height_only(self):
        import PIL.Image
        image = PIL.Image.new('L', (50, 60))
        crop = self.center_crop(image, 100, 30)
        self.assertEqual(crop.size, (50, 30))

    def test_center_horizontally(self):
        # Test by drawing a centered red rectangle, and checking there is
        # no black after cropping.
        import PIL.Image
        import PIL.ImageDraw
        image = PIL.Image.new('L', (100, 100))
        draw = PIL.ImageDraw.Draw(image)
        draw.rectangle((25, 0, 76, 100), fill='#ff0000')
        self.assertNotEqual(image.getcolors(), [(5000, 76)])
        crop = self.center_crop(image, 50, 100)
        self.assertEqual(crop.getcolors(), [(5000, 76)])

    def test_center_vertically(self):
        # Test by drawing a centered red rectangle, and checking there is
        # no black after cropping.
        import PIL.Image
        import PIL.ImageDraw
        image = PIL.Image.new('L', (100, 100))
        draw = PIL.ImageDraw.Draw(image)
        draw.rectangle((0, 25, 100, 76), fill='#ff0000')
        self.assertNotEqual(image.getcolors(), [(5000, 76)])
        crop = self.center_crop(image, 100, 50)
        self.assertEqual(crop.getcolors(), [(5000, 76)])


class scale_pil_image_tests(unittest.TestCase):
    def scale_pil_image(self, *a, **kw):
        from s4u.image.scale import scale_pil_image
        return scale_pil_image(*a, **kw)

    def _make_image(self, width, height):
        import PIL.Image
        return PIL.Image.new('L', (width, height))

    def test_width_or_height_required(self):
        self.assertRaises(ValueError, self.scale_pil_image, None, None, None)

    def test_scale_to_width_only(self):
        image = self._make_image(50, 60)
        scale = self.scale_pil_image(image, width=25)
        self.assertEqual(scale.size, (25, 30))

    def test_scale_to_height_only(self):
        image = self._make_image(50, 30)
        scale = self.scale_pil_image(image, height=60)
        self.assertEqual(scale.size, (100, 60))

    def test_scale_with_same_aspect_ratio(self):
        image = self._make_image(50, 50)
        scale = self.scale_pil_image(image, width=25, height=25, crop=False)
        self.assertEqual(scale.size, (25, 25))

    def test_scale_overly_wide_image_without_crop(self):
        image = self._make_image(100, 10)
        scale = self.scale_pil_image(image, width=30, height=30, crop=False)
        self.assertEqual(scale.size, (30, 3))

    def test_scale_overly_wide_image_with_crop(self):
        image = self._make_image(100, 10)
        scale = self.scale_pil_image(image, width=30, height=30, crop=True)
        self.assertEqual(scale.size, (30, 30))

    def test_scale_overly_tall_image_without_crop(self):
        image = self._make_image(10, 100)
        scale = self.scale_pil_image(image, width=30, height=30, crop=False)
        self.assertEqual(scale.size, (3, 30))

    def test_scale_overly_tall_image_with_crop(self):
        image = self._make_image(10, 100)
        scale = self.scale_pil_image(image, width=30, height=30, crop=True)
        self.assertEqual(scale.size, (30, 30))
