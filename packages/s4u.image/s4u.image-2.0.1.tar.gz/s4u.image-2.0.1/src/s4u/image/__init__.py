from s4u.image.model import Image
from s4u.image.model import ImageScale


def configure(original_path, scale_path):
    """Configure the filesystem paths used to store image files.

    :param original_path: filesystem path used for full size images.
    :param scale_path: filesystem path used for scaled images.
    """
    Image.root_path = original_path
    ImageScale.root_path = scale_path


def includeme(config):
    """Configure s4u.image using a Pyramid :py:class:`Configurator
    <pyramid.config.Configurator>` object. This will take the filesystem
    paths from the application settings using the keys
    ``fs.images.original`` and ``fs.images.scaled``.
    """
    settings = config.registry.settings
    configure(settings['fs.images.original'],
              settings['fs.images.scaled'])
    for key in ['original', 'scaled']:
        base_url = settings.get('fs.images.%s.url' % key)
        if base_url:
            config.add_static_view(base_url,
                    settings['fs.images.%s' % key])
        else:
            config.add_static_view('image-%s' % key,
                    settings['fs.images.%s' % key],
                    cache_max_age=86400 * 31)
