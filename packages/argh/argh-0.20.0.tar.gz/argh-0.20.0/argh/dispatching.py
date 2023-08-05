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
Dispatching
~~~~~~~~~~~
"""
import argparse
import sys
from types import GeneratorType

from argh.six import text_type, BytesIO, StringIO, PY3

from argh.constants import (ATTR_NO_NAMESPACE, ATTR_WRAPPED_EXCEPTIONS,
                            ATTR_INFER_ARGS_FROM_SIGNATURE)
from argh.completion import autocomplete
from argh.assembling import add_commands, set_default_command
from argh.exceptions import CommandError
from argh import io


__all__ = ['dispatch', 'dispatch_command', 'dispatch_commands']


def dispatch(parser, argv=None, add_help_command=True,
             completion=True, pre_call=None, output_file=sys.stdout,
             raw_output=False, namespace=None):
    """Parses given list of arguments using given parser, calls the relevant
    function and prints the result.

    The target function should expect one positional argument: the
    :class:`argparse.Namespace` object. However, if the function is decorated with
    :func:`~argh.decorators.plain_signature`, the positional and named
    arguments from the namespace object are passed to the function instead
    of the object itself.

    :param parser:

        the ArgumentParser instance.

    :param argv:

        a list of strings representing the arguments. If `None`, ``sys.argv``
        is used instead. Default is `None`.

    :param add_help_command:

        if `True`, converts first positional argument "help" to a keyword
        argument so that ``help foo`` becomes ``foo --help`` and displays usage
        information for "foo". Default is `True`.

    :param output_file:

        A file-like object for output. If `None`, the resulting lines are
        collected and returned as a string. Default is ``sys.stdout``.

    :param raw_output:

        If `True`, results are written to the output file raw, without adding
        whitespaces or newlines between yielded strings. Default is `False`.

    :param completion:

        If `True`, shell tab completion is enabled. Default is `True`. (You
        will also need to install it.)  See :mod:`argh.completion`.

    By default the exceptions are not wrapped and will propagate. The only
    exception that is always wrapped is :class:`~argh.exceptions.CommandError`
    which is interpreted as an expected event so the traceback is hidden.
    You can also mark arbitrary exceptions as "wrappable" by using the
    :func:`~argh.decorators.wrap_errors` decorator.
    """
    if completion:
        autocomplete(parser)

    if argv is None:
        argv = sys.argv[1:]

    if add_help_command:
        if argv and argv[0] == 'help':
            argv.pop(0)
            argv.append('--help')

    # this will raise SystemExit if parsing fails
    args = parser.parse_args(argv, namespace=namespace)

    if hasattr(args, 'function'):
        if pre_call:  # XXX undocumented because I'm unsure if it's OK
            # Actually used in real projects:
            # * https://google.com/search?q=argh+dispatch+pre_call
            # * https://github.com/madjar/aurifere/blob/master/aurifere/cli.py#L92
            pre_call(args)
        lines = _execute_command(args)
    else:
        # no commands declared, can't dispatch; display help message
        lines = [parser.format_usage()]

    if output_file is None:
        # user wants a string; we create an internal temporary file-like object
        # and will return its contents as a string
        f = StringIO() if PY3 else BytesIO()
    else:
        # normally this is stdout; can be any file
        f = output_file

    for line in lines:
        # print the line as soon as it is generated to ensure that it is
        # displayed to the user before anything else happens, e.g.
        # raw_input() is called

        io.dump(line, f)
        if not raw_output:
            # in most cases user wants on message per line
            io.dump('\n', f)

    if output_file is None:
        # user wanted a string; return contents of our temporary file-like obj
        f.seek(0)
        return f.read()


def _execute_command(args):
    """Asserts that ``args.function`` is present and callable. Tries different
    approaches to calling the function (with an `argparse.Namespace` object or
    with ordinary signature). Yields the results line by line.

    If :class:`~argh.exceptions.CommandError` is raised, its message is
    appended to the results (i.e. yielded by the generator as a string).
    All other exceptions propagate unless marked as wrappable
    by :func:`wrap_errors`.
    """
    assert hasattr(args, 'function') and hasattr(args.function, '__call__')

    # the function is nested to catch certain exceptions (see below)
    def _call():
        # Actually call the function
        infer = getattr(args.function, ATTR_INFER_ARGS_FROM_SIGNATURE, False)
        infer_deprecated = getattr(args.function, ATTR_NO_NAMESPACE, False)
        if infer or infer_deprecated:
            # filter the namespace variables so that only those expected by the
            # actual function will pass
            f = args.function
            if hasattr(f, 'func_code'):
                # Python 2
                expected_args = f.func_code.co_varnames[:f.func_code.co_argcount]
            else:
                # Python 3
                expected_args = f.__code__.co_varnames[:f.__code__.co_argcount]

            def _normalize_keys(pairs):
                return dict((k.replace('-','_'),v) for k,v in pairs)
            normalized_kwargs = _normalize_keys(args._get_kwargs())

            ok_args = [x for x in args._get_args() if x in expected_args]
            ok_kwargs = dict((k,v) for k,v in normalized_kwargs.items()
                             if k in expected_args)

            result = args.function(*ok_args, **ok_kwargs)
        else:
            result = args.function(args)

        # Yield the results
        if isinstance(result, (GeneratorType, list, tuple)):
            # yield each line ASAP, convert CommandError message to a line
            for line in result:
                yield line
        else:
            # yield non-empty non-iterable result as a single line
            if result is not None:
                yield result

    wrappable_exceptions = [CommandError]
    wrappable_exceptions += getattr(args.function, ATTR_WRAPPED_EXCEPTIONS, [])

    try:
        result = _call()
        for line in result:
            yield line
    except tuple(wrappable_exceptions) as e:
        yield text_type(e)


def dispatch_command(function, *args, **kwargs):
    """ A wrapper for :func:`dispatch` that creates a one-command parser.

    This::

        dispatch_command(foo)

    ...is a shortcut for::

        parser = ArgumentParser()
        set_default_command(parser, foo)
        dispatch(parser)

    This function can be also used as a decorator.
    """
    parser = argparse.ArgumentParser()
    set_default_command(parser, function)
    dispatch(parser, *args, **kwargs)


def dispatch_commands(functions, *args, **kwargs):
    """ A wrapper for :func:`dispatch` that creates a parser, adds commands to
    the parser and dispatches them.

    This::

        dispatch_commands([foo, bar])

    ...is a shortcut for::

        parser = ArgumentParser()
        add_commands(parser, [foo, bar])
        dispatch(parser)

    """
    parser = argparse.ArgumentParser()
    add_commands(parser, functions)
    dispatch(parser, *args, **kwargs)
