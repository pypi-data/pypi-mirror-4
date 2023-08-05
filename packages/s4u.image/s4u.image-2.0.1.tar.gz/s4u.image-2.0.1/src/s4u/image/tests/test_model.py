import unittest
from s4u.image.testing import ImageTestCase


class generate_path_tests(unittest.TestCase):
    def generate_path(self, *a, **kw):
        from s4u.image.model import generate_path
        return generate_path(*a, **kw)

    def test_three_levels(self):
        import os
        path = self.generate_path('.xys')
        self.assertEqual(len(path.split(os.path.sep)), 3)

    def test_keep_extension(self):
        path = self.generate_path('.xyz')
        self.assertTrue(path.endswith('.xyz'))
        self.assertTrue(not path.endswith('..xyz'))


class ImageTests(ImageTestCase):
    def Image(self, *a, **kw):
        from s4u.image.model import Image
        return Image(*a, **kw)

    def ImageScale(self, *a, **kw):
        from s4u.image.model import ImageScale
        return ImageScale(*a, **kw)

    def test_init_extension_from_filename(self):
        from s4u.image.testing import PNG
        image = self.Image(PNG, 'test.gif')
        self.assertTrue(image.path.endswith('.gif'))

    def test_init_extension_from_data_if_filename_without_extension(self):
        from s4u.image.testing import PNG
        image = self.Image(PNG, 'test')
        self.assertTrue(image.path.endswith('.png'))

    def test_init_extension_from_data_if_no_filename(self):
        from s4u.image.testing import PNG
        image = self.Image(PNG)
        self.assertTrue(image.path.endswith('.png'))

    def test_init_url_only(self):
        image = self.Image(url='http://media.example.com')
        self.assertEqual(image.url, 'http://media.example.com')
        self.assertEqual(image.path, None)

    def test_init_no_data_or_url(self):
        self.assertRaises(ValueError, self.Image)

    def test_filesystem_path_not_configured(self):
        from s4u.image.testing import PNG
        from s4u.image import configure
        image = self.Image(PNG)
        configure(None, None)  # Undo test setup
        self.assertRaises(AttributeError, getattr, image, 'filesystem_path')

    def test_filesystem_path_remote_image(self):
        image = self.Image(url='http://example.com/')
        self.assertEqual(image.filesystem_path, None)

    def test_download_already_local(self):
        from s4u.image.testing import PNG
        image = self.Image(PNG)
        self.assertRaises(TypeError, image.download)

    def test_download_png_image(self):
        from s4u.image.testing import PNG
        import mock
        image = self.Image(url='http://example.com/')
        response = mock.Mock()
        response.content = PNG
        with mock.patch('requests.get', return_value=response):
            image.download()
            self.assertTrue(image.path.endswith('.png'))

    def test_scale_no_size(self):
        from s4u.image.testing import PNG
        image = self.Image(PNG)
        self.assertRaises(ValueError, image.scale, 0, 0)

    def test_scale_remote_image_not_possible(self):
        image = self.Image(url='http://example.com/')
        self.assertRaises(TypeError, image.scale, 150)

    def test_scale_existing_scale(self):
        from s4u.sqlalchemy import meta
        from s4u.image.testing import PNG
        session = meta.Session()
        image = self.Image(PNG)
        session.add(image)
        session.flush()
        scale = self.ImageScale(image, width=123)
        session.add(scale)
        result = image.scale(width=123)
        self.assertTrue(result is scale)

    def test_scale_to_new_scale(self):
        from s4u.sqlalchemy import meta
        from s4u.image.testing import PNG
        from s4u.image.model import ImageScale
        session = meta.Session()
        image = self.Image(PNG)
        session.add(image)
        result = image.scale(width=123)
        self.assertTrue(isinstance(result, ImageScale))
        self.assertEqual(result.param_width, 123)
        self.assertEqual(result.param_height, 0)
        self.assertEqual(result.param_crop, False)


class ImageScaleTests(ImageTestCase):
    def Image(self, *a, **kw):
        from s4u.image.model import Image
        return Image(*a, **kw)

    def ImageScale(self, *a, **kw):
        from s4u.image.model import ImageScale
        return ImageScale(*a, **kw)

    def test_init_extension_based_on_image_type(self):
        from s4u.image.testing import JPEG
        from s4u.image.testing import PNG
        image = self.Image(JPEG)
        scale = self.ImageScale(image, 10)
        self.assertTrue(scale.path.endswith('.jpeg'))
        image = self.Image(PNG)
        scale = self.ImageScale(image, 10)
        self.assertTrue(scale.path.endswith('.png'))

    def test_filesystem_path_not_configured(self):
        from s4u.image import configure
        from s4u.image.testing import PNG
        image = self.Image(PNG)
        scale = self.ImageScale(image, 1)
        configure(None, None)  # Undo test setup
        self.assertRaises(AttributeError, getattr, scale, 'filesystem_path')
