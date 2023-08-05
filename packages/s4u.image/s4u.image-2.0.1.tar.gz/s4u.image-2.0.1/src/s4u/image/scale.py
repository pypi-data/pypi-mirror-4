from cStringIO import StringIO
import PIL.Image
import PIL.ImageChops
import PIL.ImageFile

# Set a larger buffer size. This fixes problems with jpeg decoding.
# See http://mail.python.org/pipermail/image-sig/1999-August/000816.html for
# details.
PIL.ImageFile.MAXBLOCK = 1000000


def scale_image(image, width=None, height=None, crop=False,
        strip_whitespace=False):
    """Scale the given image data to another size and return the result
    as a string or optionally write in to the file-like `result` object.

    :param file image: open file for image to scale
    :param int width: desired maximum image width
    :param int height: desired maximum image width
    :param bool crop: allow cropping image to fill full width and height
    :param bool strip_whitespace: crop surrounding whitespace before
      processing the image

    The return value is a tuple with the new image, the image format and
    a size-tuple.

    The `width`, `height`, `direction` parameters will be passed to
    :meth:`scale_pil_image`, which performs the actual scaling.
    """
    image = PIL.Image.open(image)

    # When we create a new image during scaling we loose the format
    # information, so remember it here.
    format = image.format
    if format == 'GIF':
        format = 'PNG'
    elif format != 'PNG':
        format = 'JPEG'

    if strip_whitespace:
        image = crop_surrounding_whitespace(image)

    image = scale_pil_image(image, width, height, crop)
    output = StringIO()
    image.save(output, format, optimize=True)
    return (output.getvalue(), format, image.size)


def correct_colour_mode(image):
    """Make sure an image uses a colour handling scheme which allows for
    high quality scaling and can be rendered by web browsers.
    """
    if image.mode == '1':
        # Convert black&white to grayscale
        image = image.convert("L")
    elif image.mode == 'P':
        # Convert palette based images to 3x8bit+alpha
        image = image.convert('RGBA')
    elif image.mode == 'CMYK':
        # Convert CMYK to RGB since web browser can not handle CMYK
        image = image.convert('RGB')
    return image


def crop_surrounding_whitespace(image):
    """Remove surrounding empty space around an image.

    This implemenation assumes that the surrounding space has the same colour
    as the top leftmost pixel.

    :param image: PIL image
    :rtype: PIL image
    """
    bg = PIL.Image.new(image.mode, image.size, image.getpixel((0, 0)))
    diff = PIL.ImageChops.difference(image, bg)
    bbox = diff.getbbox()
    if not bbox:
        return image

    # XXX: if we want to crop the final image we should try to match the
    # desired aspect ratio here to make sure the last step will not
    # crop out real image data.
    return image.crop(bbox)


def center_crop(image, width, height):
    """Crop an image to the desired width and height. The crop is
    made from the middle of the image.

    :param image: PIL image
    :param int width: maximum width, or None of width is unrestrained
    :param int height: maximum height, or None of height is unrestrained
    :rtype: PIL image
    """
    (current_width, current_height) = image.size

    if width is not None and current_width > width:
        left = int((current_width - width) / 2.0)
        right = left + width
    else:
        left = 0
        right = current_width

    if height is not None and current_height > height:
        top = int((current_height - height) / 2.0)
        bottom = top + height
    else:
        top = 0
        bottom = current_height

    return image.crop((left, top, right, bottom))


def scale_pil_image(image, width=None, height=None, crop=False):
    """Scale a PIL image to another size.

    :param image: PIL Image instance
    :param int width: desired maximum image width
    :param int height: desired maximum image width
    :param bool crop: allow cropping image to fill full width and height
    :rtype: PIL Image

    The generated image is a JPEG image, unless the original is a GIF or PNG
    image. This is needed to make sure alpha channel information is not lost,
    which JPEG does not support.
    """
    if width is None and height is None:
        raise ValueError('Either width or height need to be given')

    image = correct_colour_mode(image)

    (current_width, current_height) = image.size

    scale_height = (float(height) / float(current_height)) \
            if height is not None else None
    scale_width = (float(width) / float(current_width)) \
            if width is not None else None

    if scale_height == scale_width:
        # The original already has the right aspect ratio, so use a fast
        # thumbnail to scale.
        image.thumbnail((width, height), PIL.Image.ANTIALIAS)
        return image

    if crop:
        scale = max(scale_width, scale_height)
    else:
        scale = min(filter(None, [scale_width, scale_height]))

    # Skip scale multiplication if possible to prevent off-by-one errors
    new_width = width if scale == scale_width \
            else int(current_width * scale)
    new_height = height if scale == scale_height \
            else int(current_height * scale)

    image.draft(image.mode, (new_width, new_height))
    image = image.resize((new_width, new_height), PIL.Image.ANTIALIAS)

    if not crop:
        return image

    return center_crop(image, width, height)
