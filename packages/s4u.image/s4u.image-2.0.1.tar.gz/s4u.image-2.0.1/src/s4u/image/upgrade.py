import os
from sqlalchemy import schema
from sqlalchemy import types
from s4u.upgrade import upgrade_context
from s4u.upgrade import upgrade_step
from s4u.image import configure
from s4u.sqlalchemy import meta
from sqlalchemy.engine.reflection import Inspector


@upgrade_context('image',
        [('--fs-images-original',
            {'type': str, 'required': True, 'dest': 'fs_images_original'}),
         ('--fs-images-scaled',
            {'type': str, 'required': True, 'dest': 'fs_images_scaled'})])
def setup_image_paths(options):
    configure(options.fs_images_original, options.fs_images_scaled)
    return {'fs.images.original': options.fs_images_original,
            'fs.images.scaled': options.fs_images_scaled}


@upgrade_step(require=['image'])
def create_directories(environment):
    _create_directories(environment['fs.images.original'])
    _create_directories(environment['fs.images.scaled'])


def _create_directories(root_path):
    if not os.path.isdir(root_path):
        raise RuntimeError('%s is not a valid image root path' % root_path)
    for top in xrange(16):
        top_path = os.path.join(root_path, '%x' % top)
        if not os.path.exists(top_path):
            os.mkdir(top_path)
        for sub in xrange(256):
            sub_path = os.path.join(top_path, '%02x' % sub)
            if not os.path.exists(sub_path):
                os.mkdir(sub_path)


@upgrade_step(require=['sql'])
def add_missing_entities(environment):  # pragma: no cover
    engine = environment['sql-engine']
    meta.metadata.create_all(engine)


@upgrade_step(require=['sql'])
def add_url_column(environment):
    engine = environment['sql-engine']
    alembic = environment['alembic']
    inspector = Inspector.from_engine(engine)
    columns = set(c['name']
                  for c in inspector.get_columns('image'))
    if 'url' not in columns:
        alembic.add_column('image', schema.Column('url', types.Text()))
