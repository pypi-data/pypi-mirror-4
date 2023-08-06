==========
Change log
==========

Version 2.5
===========

* The PilImage wrapper is more transparent - you can use any methods or
  attributes available to the underlying PIL Image instance.

* Fixed the first column of the QR Code coming up empty! Thanks to BecoKo.


Version 2.4
===========

* Use a pluggable backend system for generating images, thanks to Branko Čibej!
  Comes with PIL and SVG backends built in.

Version 2.4.1
-------------

* Fix a packaging issue

Version 2.4.2
-------------

* Added a ``show`` method to the PIL image wrapper so the ``run_example``
  function actually works.


Version 2.3
===========

* When adding data, auto-select the more efficient encoding methods for numbers
  and alphanumeric data (KANJI still not supported).

Version 2.3.1
-------------

* Encode unicode to utf-8 bytestrings when adding data to a QRCode.


Version 2.2
===========

* Fixed tty output to work on both white and black backgrounds.

* Added `border` parameter to allow customizing of the number of boxes used to
  create the border of the QR code


Version 2.1
===========

* Added a ``qr`` script which can be used to output a qr code to the tty using
  background colors, or to a file via a pipe.
