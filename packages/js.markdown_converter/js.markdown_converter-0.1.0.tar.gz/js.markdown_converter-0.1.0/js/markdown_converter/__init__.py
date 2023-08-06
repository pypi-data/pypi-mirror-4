#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# js.markdown_converter
#----------------------------------------------------------------------
# Copyright (c) 2013 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under
# the terms of the LICENCE attached in the distribution package.
#
# Created on 2013-04-19

from fanstatic import Library, Resource

__author__ = "Manuel Vázquez Acosta <mva.led@gmail.com>"
__date__   = "Fri Apr 19 17:16:51 2013"


lib = Library('js.markdown_converter', 'resources')
markdown_converter = Resource(lib,
                              'Markdown.Converter.js',
                              minified='Markdown.Converter.min.js',
                              bottom=True)


__all__ = ('markdown_converter', )

del Library, Resource
