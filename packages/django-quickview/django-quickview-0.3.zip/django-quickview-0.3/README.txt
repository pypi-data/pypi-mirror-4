=========
QuickView
=========

- Author: Thomas Augestad Weholt, <thomas@weholt.org>.
- License: Modified BSD.
- Source: https://bitbucket.org/weholt/django-quickview/src
- Package: https://pypi.python.org/pypi/django-quickview/

- Requirements:
    - Django 1.5
    - Python 2.7.x or 3.3

Read more at https://bitbucket.org/weholt/django-quickview/src/fde97a0a0befaeda0ab2317035f8e7cd9c311511/docs/basic.md?at=default

Version history
---------------

0.3     - Fleshed out some docs, fixed some bugs, cleaned up code.

0.2     - Refactored code; QuickView is not dependent on a model. A subclass of QuickView named ModelQuickView takes
          care of all model related magic. This makes it easier to write non-model based views based on the same concept.

0.1     - Initial release.