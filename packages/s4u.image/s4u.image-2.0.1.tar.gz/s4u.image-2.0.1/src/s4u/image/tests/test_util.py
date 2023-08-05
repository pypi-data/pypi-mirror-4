import unittest


class extension_for_image_data_tests(unittest.TestCase):
    def extension_for_image_data(self, *a, **kw):
        from s4u.image.util import extension_for_image_data
        return extension_for_image_data(*a, **kw)

    def test_invalid_image(self):
        import StringIO
        input = StringIO.StringIO('invalid')
        self.assertRaises(ValueError,
                self.extension_for_image_data, input)

    def test_minimal_gif(self):
        import StringIO
        from s4u.image.testing import GIF
        input = StringIO.StringIO(GIF)
        self.assertEqual(self.extension_for_image_data(input), '.gif')

    def test_minimal_png(self):
        import StringIO
        from s4u.image.testing import PNG
        input = StringIO.StringIO(PNG)
        self.assertEqual(self.extension_for_image_data(input), '.png')
