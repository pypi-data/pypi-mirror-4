import unittest


class configure_tests(unittest.TestCase):
    def configure(self, *a, **kw):
        from s4u.image import configure
        return configure(*a, **kw)

    def test_set_original_path(self):
        from s4u.image.model import Image
        self.assertEqual(Image.root_path, None)
        try:
            self.configure('/tmp', None)
            self.assertEqual(Image.root_path, '/tmp')
        finally:
            Image.root_path = None

    def test_set_scale_path(self):
        from s4u.image.model import ImageScale
        self.assertEqual(ImageScale.root_path, None)
        try:
            self.configure(None, '/tmp')
            self.assertEqual(ImageScale.root_path, '/tmp')
        finally:
            ImageScale.root_path = None


class includeme_tests(unittest.TestCase):
    def includeme(self, *a, **kw):
        from s4u.image import includeme
        return includeme(*a, **kw)

    def test_set_original_path(self):
        from s4u.image.model import Image
        config = MockConfig({'fs.images.original': '/tmp',
                             'fs.images.scaled': None})
        self.assertEqual(Image.root_path, None)
        self.includeme(config)
        self.assertEqual(Image.root_path, '/tmp')

    def test_set_scale_path(self):
        from s4u.image.model import ImageScale
        config = MockConfig({'fs.images.original': None,
                             'fs.images.scaled': '/tmp'})
        self.assertEqual(ImageScale.root_path, None)
        self.includeme(config)
        self.assertEqual(ImageScale.root_path, '/tmp')

    def test_setup_static_views(self):
        config = MockConfig({'fs.images.original': '/fs/original',
                             'fs.images.scaled': '/fs/scaled'})
        self.includeme(config)
        self.assertEqual(len(config.static_views), 2)
        self.assertEqual(config.static_views[0]['path'], '/fs/original')
        self.assertTrue(config.static_views[0]['cache_max_age'] > 86400)
        self.assertEqual(config.static_views[1]['path'], '/fs/scaled')
        self.assertTrue(config.static_views[1]['cache_max_age'] > 86400)

    def test_setup_static_views_with_external_url(self):
        config = MockConfig({'fs.images.original': '/fs/original',
                             'fs.images.scaled': '/fs/scaled',
                             'fs.images.scaled.url': 'http://media.com/'})
        self.includeme(config)
        self.assertEqual(len(config.static_views), 2)
        self.assertEqual(config.static_views[0]['path'], '/fs/original')
        self.assertEqual(config.static_views[1]['name'], 'http://media.com/')
        self.assertEqual(config.static_views[1]['path'], '/fs/scaled')
        self.assertTrue('cache_max_age' not in config.static_views[1])


class MockRegistry:
    pass


class MockConfig:
    def __init__(self, settings):
        self.registry = MockRegistry()
        self.registry.settings = settings
        self.static_views = []

    def add_static_view(self, name, path, **kw):
        info = kw
        info['name'] = name
        info['path'] = path
        self.static_views.append(info)
