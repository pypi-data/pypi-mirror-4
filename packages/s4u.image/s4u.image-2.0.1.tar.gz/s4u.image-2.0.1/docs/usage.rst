Usage
=====

Before you can use s4u.image you need tell it where it can store image data on
disk. This is done by calling :py:func:`s4u.image.configure`.

.. code-block:: python

   from s4u.image import configure

   configure('/var/lib/photos/fullsize', '/var/lib/photos/scaled')

If you are using `Pyramid <http://docs.pylonsproject.org/docs/pyramid.html>`_
application you can also configure s4u.image using Pyramid's Configurator
object. When doing this the paths will be taken from the application settings
using the keys ``fs.images.original`` and ``fs.images.scaled``.

.. code-block:: python

   from pyramid.config import Configurator

   config = Configurator()
   config.include('s4u.image')

Images stored using :py:class:`s4u.image.model.Image` objects. When creating
an image you need to pass in the raw image data, and optionally a filename.
The filename is only used determine the extension for the image file that will
be created.

.. code-block:: python

   from s4u.sqlalchemy import meta
   from s4u.image.model import Image

   def load_image(filename):
       session = meta.Session()
       image = Image(open(filename).read(), filename)
       session.add(image)
       return image

An image has two useful properties:
:py:attr:`path <s4u.image.model.Image.path>` which contains the filename
for the image relative to the directories where all images are stored,
and :py:attr:`filesystem_path <s4u.image.model.Image.filesystem_path>` which
contains the full filesystem path of the image.

Most of the time you do not want to use the full size image, but scaled to a
specific width or height. This is handled by the :py:meth:`scale 
<s4u.image.model.Image.scale>` method.

.. code-block:: python

   image = load_image('mugshot.png')
   # Scale to maximum of 50x100 pixels
   scale = image.scale(width=50, height=100)

This will return a :py:class:`ImageScale <s4u.image.model.ImageScale>` object
which contains a scaled version of the image. Scaled images are stored
automatically, so an image will never be scaled twice to the same dimensions.
