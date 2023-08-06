#!/usr/bin/env python

try:
    from qargparse import get, parse
except ImportError as E:
    # I should import qoptparse here as a fallback
    # but... just reraise now
    raise E

__all__ = ['get', 'parse']
