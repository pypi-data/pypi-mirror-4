Changelog
=========

2.0.1 - January 8, 2013
-----------------------

- First public release.


2.0 - September 14, 2012
------------------------

- Add a new URL column to images and extend API to support remote images.

- Use Pillow instead of PIL.


2.0a3 - August 3, 2012
----------------------

- Fix bug in image scale generation which ignored the whitespace option.
  Thanks to Jason for catching this.

2.0a2 - August 3, 2012
----------------------

- Fix error in storing image scale parameters.


2.0a1 - August 3, 2012
----------------------

- Add option to remove whitespace surrounding an image.


1.4 - February 28, 2012
-----------------------

- Add support for hosting images via a separate URL.


1.3 - November 30, 2011
-----------------------

- Add a better index for index for the image scale table.


1.2 - October 14, 2011
----------------------

- Add support for s4u.upgrade: add an upgrade step to create the image
  directories.

- Only use 16 top-level directories; 256 was a bit too much.


1.1 - September 28, 2011
------------------------

- Move minimal image data to s4u.image.testing to promote reuse by other
  packages.

- Register a static view for Pyramid to serve image data.


1.0 - August 8, 2011
--------------------

- First version.
