Introduction
============

Fanstatic_ resource definition for Markdown.Converter. The
``Markdown.Converter`` object takes a text written in markdown and returns
HTML.

To use in your WSGI ``fanstatic`` resourced application just need the
``markdown_converter`` resource::

    >>> from js.markdown_converter import markdown_converter
    >>> markdown_converter.need()

.. _Fanstatic: https://pypi.python.org/pypi/fanstatic/


Copyright and License
=====================

This is just a packaging of a JS file taken from IPython's code base.

The copyright for the packaging goes to Merchise Autrement. But the authors of
the Markdown.Convert.js hold the copyright for their code::


      Packaging of the Markdown.Converter.js taken from IPython's code base
      (c) 2013 Merchise Autrement

      This program is free software: you can redistribute it and/or modify it
      under the terms of the GNU General Public License as published by the
      Free Software Foundation, either version 3 of the License, or (at your
      option) any later version.

      This program is distributed in the hope that it will be useful, but
      WITHOUT ANY WARRANTY; without even the implied warranty of
      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
      Public License for more details.  You should have received a copy of the
      GNU General Public License along with this program.  If not, see
      http://www.gnu.org/licenses/.

..  LocalWords:  Fanstatic fanstatic
