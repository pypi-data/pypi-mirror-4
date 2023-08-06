# coding: utf-8
"""
Silence chosen exceptions.

Author: João Bernardo Oliveira - @jbvsmo

Replacement for the idiom:
    
>>> try:
...     may_raise_exception()
... except Exception:
...     pass

Just write:

>>> with stfu:
...     may_raise_exception()

>>> with stfu(TypeError, ValueError):
...     may_raise_exception()


To catch *everything* (even KeyboardInterrup and StopIteration):

>>> with stfu_all:
...     may_raise_any_exception()


"Errors should never pass silently.
 Unless explicitly silenced." :)

"""

__all__ = 'stfu', 'stfu_all'

class STFU:
    """ Silence chosen exceptions.
        Use the `stfu` instance directly.
    """
    def __init__(self, *args):
        self.cls = args or None
    def __enter__(self):
        return self
    def __call__(self, *args):
        return type(self)(*args)
    def __exit__(self, cls, exc, trace):
        if self.cls is None or issubclass(cls, self.cls):
            return True

stfu = STFU(Exception)
stfu_all = STFU()

