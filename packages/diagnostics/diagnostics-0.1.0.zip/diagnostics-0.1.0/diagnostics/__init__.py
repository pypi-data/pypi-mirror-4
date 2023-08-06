# -*- coding: utf8 -*-

from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals

import sys

from .models import ExceptionInfo
from .storages import FileStorage
from .formatters import HtmlFormatter
from ._py3k import to_unicode


__author__ = "Michal Belica"
__version__ = "0.1.0"


class _ExceptionHook(object):
    def __init__(self):
        self.storage = None
        self.formatter = None

    def enable(self, storage=None, formatter=HtmlFormatter()):
        if not storage:
            storage = FileStorage()

        self.storage = storage
        self.formatter = formatter

        sys.excepthook = self

    def __call__(self, type, value, traceback):
        exception_info = ExceptionInfo.from_values(type, value, traceback)

        try:
            data = self.formatter.format_exception(exception_info)
        except:
            data = "<p><pre>%s\n%s</pre></p>" % (
                to_unicode(exception_info),
                to_unicode(ExceptionInfo.new()),
            )

        self.storage.save(data, exception_info)


exception_hook = _ExceptionHook()
