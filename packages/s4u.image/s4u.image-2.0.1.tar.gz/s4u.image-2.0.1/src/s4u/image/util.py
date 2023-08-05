import PIL.Image


def extension_for_image_data(data):
    '''Determine a suitable filesystem extension for image data. The extension
    is based on the image format.

    :param data: either a filename for an image file, or an open file handle.
    :return: extension including leading dot
    '''
    try:
        image = PIL.Image.open(data)
        image.load()
    except (IOError, OverflowError):
        raise ValueError('Not a valid image')

    return '.%s' % image.format.lower()
