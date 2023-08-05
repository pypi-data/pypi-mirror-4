# -*- coding: utf-8 -*-
#
#  Copyright (c) 2010—2012 Andrey Mikhailenko and contributors
#
#  This file is part of Argh.
#
#  Argh is free software under terms of the GNU Lesser
#  General Public License version 3 (LGPLv3) as published by the Free
#  Software Foundation. See the file README for copying conditions.
#
"""
Output Processing
~~~~~~~~~~~~~~~~~
"""
import locale

from argh.six import binary_type, text_type, PY3


__all__ = ['dump', 'encode_output', 'safe_input']


def _input(prompt):
    # this function can be mocked up in tests
    if PY3:
        return input(prompt)
    else:
        return raw_input(prompt)


def safe_input(prompt):
    "Prompts user for input. Correctly handles prompt message encoding."

    if PY3:
        if not isinstance(prompt, text_type):
            # Python 3.x: bytes →  unicode
            prompt = prompt.decode()
    else:
        if isinstance(prompt, text_type):
            # Python 2.x: unicode →  bytes
            encoding = locale.getpreferredencoding() or 'utf-8'
            prompt = prompt.encode(encoding)

    return _input(prompt)


def encode_output(value, output_file):
    """ Encodes given value so it can be written to given file object.

    Value may be Unicode, binary string or any other data type.

    The exact behaviour depends on the Python version:

    Python 3.x

        `sys.stdout` is a `_io.TextIOWrapper` instance that accepts `str`
        (unicode) and breaks on `bytes`.

        It is OK to simply assume that everything is Unicode unless special
        handling is introduced in the client code.

        Thus, no additional processing is performed.

    Python 2.x

        `sys.stdout` is a file-like object that accepts `str` (bytes)
        and breaks when `unicode` is passed to `sys.stdout.write()`.

        We can expect both Unicode and bytes. They need to be encoded so as
        to match the file object encoding.

        The output is binary if the object is a TTY; otherwise it's Unicode.

    """
    if not PY3:
        # handle special cases in Python 2.x

        if output_file.isatty():
            # TTY expects bytes
            if isinstance(value, text_type):
                encoding = getattr(output_file, 'encoding', None)
                encoding = encoding or locale.getpreferredencoding() or 'utf-8'
                # unicode →  binary
                return value.encode(encoding)
            return binary_type(value)

        if isinstance(value, binary_type):
            # binary →  unicode
            return value.decode('utf-8')

    # whatever → unicode
    return text_type(value)


def dump(raw_data, output_file):
    """ Writes given line to given output file.
    See :func:`encode_output` for details.
    """
    data = encode_output(raw_data, output_file)
    output_file.write(data)
