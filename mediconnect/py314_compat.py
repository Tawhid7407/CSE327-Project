"""
Compatibility shim: Django 4.2.x's template Context copying on Python 3.14+.

``django.template.context.BaseContext.__copy__`` (installed with Django
4.2.11) does ``copy(super())`` to shallow-copy a Context without
re-entering its own ``__copy__``. Python 3.14 changed how ``copy.copy()``
handles ``super`` proxy objects: the call now returns an object with no
writable ``__dict__``, so the very next line (``duplicate.dicts = ...``)
raises ``AttributeError: 'super' object has no attribute 'dicts' and no
__dict__ for setting new attributes``.

Normal request handling (``manage.py runserver``) never triggers this,
since it only happens where a Context gets copy()'d - which in Django
only occurs in the test client (it copies each rendered template's
Context so that ``response.context`` works in tests). Without this
patch, every test that renders a template raises the AttributeError
above, effectively blocking Unit Testing (`manage.py test`) entirely on
this Python version.

Remove this shim once the project's Django version is upgraded to one
with a Python 3.14-compatible ``Context.__copy__`` (check the Django
changelog / this bug being fixed upstream before deleting).
"""
import django.template.context as _context


def _base_context_copy(self):
    duplicate = self.__class__.__new__(self.__class__)
    duplicate.__dict__.update(self.__dict__)
    duplicate.dicts = self.dicts[:]
    return duplicate


if not getattr(_context.BaseContext.__copy__, "_py314_patched", False):
    _base_context_copy._py314_patched = True
    _context.BaseContext.__copy__ = _base_context_copy
