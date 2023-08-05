import unittest
from s4u.sqlalchemy.testing import DatabaseTestCase


class setup_image_paths_tests(unittest.TestCase):
    def setup_image_paths(self, *a, **kw):
        from s4u.image.upgrade import setup_image_paths
        return setup_image_paths(*a, **kw)

    def test_configure_paths(self):
        import mock
        with mock.patch('s4u.image.upgrade.configure') as mock_configure:
            options = DummyOptions(
                    fs_images_original='/tmp/foo',
                    fs_images_scaled='/tmp/buz')
            self.setup_image_paths(options)
            mock_configure.assert_called_once_with('/tmp/foo', '/tmp/buz')

    def test_environment(self):
        import mock
        with mock.patch('s4u.image.upgrade.configure'):
            options = DummyOptions(
                    fs_images_original='/tmp/foo',
                    fs_images_scaled='/tmp/buz')
            environment = self.setup_image_paths(options)
            self.assertEqual(
                    environment,
                    {'fs.images.original': '/tmp/foo',
                     'fs.images.scaled': '/tmp/buz'})


class create_directories_tests(unittest.TestCase):
    def create_directories(self, *a, **kw):
        from s4u.image.upgrade import create_directories
        return create_directories(*a, **kw)

    def test_create_original_directories(self):
        import mock
        with mock.patch('s4u.image.upgrade._create_directories') as mock_crea:
            self.create_directories({'fs.images.original': '/tmp/foo',
                                     'fs.images.scaled': '/tmp/buz'})
            mock_crea.assert_has_calls([mock.call('/tmp/foo')], True)

    def test_create_scaled_directories(self):
        import mock
        with mock.patch('s4u.image.upgrade._create_directories') as mock_crea:
            self.create_directories({'fs.images.original': '/tmp/foo',
                                     'fs.images.scaled': '/tmp/buz'})
            mock_crea.assert_has_calls([mock.call('/tmp/buz')], True)


class int_create_directories_tests(unittest.TestCase):
    def _create_directories(self, *a, **kw):
        from s4u.image.upgrade import _create_directories
        return _create_directories(*a, **kw)

    def test_all_dirs_exist(self):
        import mock
        with mock.patch('os.path.exists') as mock_exists:
            with mock.patch('os.mkdir') as mock_mkdir:
                mock_exists.return_value = True
                self._create_directories('/tmp')
                self.assertEqual(mock_exists.call_count, 16 + (16 * 256))
                self.assertEqual(mock_mkdir.called, False)

    def test_toplevel_missing(self):
        import mock
        with mock.patch('os.path.isdir') as mock_isdir:
            mock_isdir.return_value = False
            self.assertRaises(RuntimeError, self._create_directories, '/')

    def test_create_all(self):
        import mock
        with mock.patch('os.path.exists') as mock_exists:
            with mock.patch('os.mkdir') as mock_mkdir:
                mock_exists.return_value = False
                self._create_directories('/tmp')
                self.assertEqual(mock_exists.call_count, 16 + (16 * 256))
                self.assertEqual(mock_mkdir.call_count, 16 + (16 * 256))



class add_url_column_tests(DatabaseTestCase):
    create_tables = False

    def add_url_column(self, *a, **kw):
        from s4u.image.upgrade import add_url_column
        return add_url_column(*a, **kw)

    def test_already_in_desired_situation(self):
        from s4u.sqlalchemy import meta
        import s4u.image.model
        s4u.image.model  # Hello PyFlakes
        meta.metadata.create_all(self.engine)
        self.add_url_column({'sql-engine': self.engine, 'alembic': None})

    def test_add_url_column(self):
        import mock
        engine = self.engine
        engine.execute(
                'CREATE TABLE image (id INT)')
        alembic = mock.Mock()
        self.add_url_column({'sql-engine': engine, 'alembic': alembic})
        self.assertEqual(alembic.add_column.call_count, 1)
        arguments = alembic.add_column.call_args
        self.assertEqual(arguments[0][0], 'image')
        self.assertEqual(arguments[0][1].name, 'url')





class DummyOptions(object):
    def __init__(self, **kw):
        for (k, v) in kw.items():
            setattr(self, k, v)
