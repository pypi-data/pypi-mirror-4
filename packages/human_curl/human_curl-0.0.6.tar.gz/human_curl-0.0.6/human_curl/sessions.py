#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
human_curl.sessions
~~~~~~~~~~~~~~~~~~~

Human curl module to store and manage sessions

:copyright: (c) 2012 by Alexandr Lispython (alex@obout.ru).
:license: BSD, see LICENSE for more details.
"""

class Session(object):
    """Human curl sessions store
    """
    def __init__(self, *args, **kwargs):
        pass


def session(**kwargs):
    return Session(**kwargs)
