API reference
=============

Configuration
-------------

.. module:: s4u.image

.. autofunction:: configure

.. autofunction:: includeme


Scaling functions
-----------------

.. module:: s4u.image.scale

.. autofunction:: scale_image

.. autofunction:: correct_colour_mode

.. autofunction:: crop_surrounding_whitespace

.. autofunction:: center_crop

.. autofunction:: scale_pil_image


Image model
-----------

.. module:: s4u.image.model

.. autoclass:: Image

   .. autoattribute:: filesystem_path

   .. automethod:: scale

.. autoclass:: ImageScale

   .. autoattribute:: width

   .. autoattribute:: height

   .. autoattribute:: filesystem_path
