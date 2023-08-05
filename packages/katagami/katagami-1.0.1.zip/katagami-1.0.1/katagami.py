#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""katagami: a simple xml/html template library
============================================

This library is one of many `Python templating libraries
<http://wiki.python.org/moin/Templating>`_.


Features
--------
 * Based on XML's Processing instructions (`<?...?>`)
 * Simple features and simple implementation
 * Python script inside XML/HTML with any level indentation
 * `Inline expression`_
 * `Embed script`_
 * `Block structure`_
 * Supports both of Python 2 and Python 3
 * As fast as `mako <http://www.makotemplates.org/>`_
 * Caching by `functools.lru_cache <http://docs.python.org/3/library/functools.html?highlight=functools.lru_cache#functools.lru_cache>`_ (only in Python 3)


Example
-------

Setup::

    >>> def _(html, encoding='utf-8'):
    ...     print(render(io.BytesIO(html)).decode(encoding))

Make a HTML string with `inline expression`_ and Python's `for` (`Block
structure`_)::

    >>> _(b'''<html>
    ... <body>
    ...     <? for name in ['world']: {?>
    ...         <p>hello, <?=name?></p>
    ...     <?}?>
    ... </body>
    ... </html>''')
    <html>
    <body>
    <BLANKLINE>
            <p>hello, world</p>
    <BLANKLINE>
    </body>
    </html>


Inline expression
-----------------

This feature evaluates your inline expression and output to result::

    >>> _(b'''<html><body>
    ...     <?='hello, world'?>
    ... </body></html>''')
    <html><body>
        hello, world
    </body></html>

By the default, this example raises an exception, evaluated expression must be
`str` (`unicode` in Python 2)::

    >>> _(b'''<html><body>
    ...     <?=1?>
    ... </body></html>''')
    Traceback (most recent call last):
    ...
    TypeError: Can't convert 'int' object to str implicitly

Set the `cast_string` feature::

    >>> _(b'''<html><body>
    ...     <?=feature cast_string="True"?>
    ...     <?=1?>
    ... </body></html>''')
    <html><body>
    <BLANKLINE>
        1
    </body></html>

Also set the `trap_exceptions` feature::

    >>> _(b'''<html><body>
    ...     <?=feature trap_exceptions="True"?>
    ...     <?=1?>
    ... </body></html>''')
    <html><body>
    <BLANKLINE>
        Can't convert 'int' object to str implicitly
    </body></html>

Note
~~~~

 * You can use `cast_string` and `trap_exceptions` simultaneously.
 * You can handle `cast_string` and `trap_exceptions` by defining the function
   `__str__`. By the default, `__str__` is `str` in Python 3 (`unicode` in
   Python 2).
 * Spaces on the both sides of the expression will be stripped. But
   '<?= feature' is a bad.
 * You can insert a comment.

Example::

    >>> _(b'''<html><body>
    ... <?py
    ...     def __str__(o):
    ...         return '__str__(%s)' % o
    ... ?>
    ...     <?=feature cast_string="True" trap_exceptions="True"?>
    ...     <?= 1 ?>
    ...     <?= notfound # get an error ?>
    ... </body></html>''')
    <html><body>
    <BLANKLINE>
    <BLANKLINE>
        __str__(1)
        __str__(name 'notfound' is not defined)
    </body></html>


Embed script
------------

All indentation will be arranged automatically::

    >>> _(b'''<html>
    ... <?py
    ...     # It is a top level here. This works fine.
    ...     if 1:
    ...         msg = 'message from indented script'
    ... ?>
    ... <body>
    ...     <p><?=msg?></p>
    ...     <?py msg = 'message from single line script' # This works fine too. ?>
    ...     <p><?=msg?></p>
    ...     <? if 1: {?>
    ... <?py
    ... # Is is nested here. This also works fine.
    ... msg = 'message from nested indented script'
    ... ?>
    ...     <p><?=msg?></p>
    ...     <?}?>
    ... </body>
    ... </html>''')
    <html>
    <BLANKLINE>
    <body>
        <p>message from indented script</p>
    <BLANKLINE>
        <p>message from single line script</p>
    <BLANKLINE>
    <BLANKLINE>
        <p>message from nested indented script</p>
    <BLANKLINE>
    </body>
    </html>


Block structure
---------------

Indentation with C-style block structure::

    >>> _(b'''<html>
    ... <body>
    ...     <p>hello,&nbsp;
    ...     <? try: {?>
    ...         <?=name?>
    ...     <?} except NameError: {?>
    ...         NameError
    ...     <?} else: {?>
    ...         never output here
    ...     <?}?>
    ...     </p>
    ... </body>
    ... </html>''')
    <html>
    <body>
        <p>hello,&nbsp;
    <BLANKLINE>
    <BLANKLINE>
            NameError
    <BLANKLINE>
        </p>
    </body>
    </html>

Note
~~~~

 * '<? }' and '{ ?>' are wrong. Don't insert space. '<?}' and '{?>' are correct.
 * Ending colon (':') is required.
 * Block closing '<?}?>' is required.


Encoding detection
------------------

Encoding will be detected automatically::

    >>> _(b'''<html>
    ... <head><meta charset="shift-jis"></head>
    ... <body>\x93\xfa\x96{\x8c\xea</body>
    ... </html>''', 'shift-jis')
    <html>
    <head><meta charset="shift-jis"></head>
    <body>\u65e5\u672c\u8a9e</body>
    </html>

Supported formats:

 * <?xml encoding="ENCODING"?>
 * <meta charset="ENCODING">
 * <meta http-equiv="Content-Type" content="MIMETYPE; ENCODING">


API
---

katagami.render
~~~~~~~~~~~~~~~

katagami.render(__file__, __encoding__=None, \*\*locals)

 * `__file__` -- `file-like object` (use `io.BytesIO 
   <http://docs.python.org/3/library/io.html?highlight=io.bytesio#io.BytesIO>`_
   for string input) or filename.
 * `__encoding__` -- Set encoding of `__file__` and the return value.
   Automatically detect the encoding if None.
 * `locals` -- local and global namespace values for template script.
 * `return` -- `bytes` in Python 3, `str` in Python 2. The return value is
   encoded by `__encoding__` or automatically detected encoding.

Rendering template flow:

    1. detect encoding
    2. decode to `str` in Python 3 (`unicode` in Python 2)
    3. translate template to Python script
    4. `compile` and `exec` the script
    5. encode result to `bytes` in Python 3 (`str` in Python 2)


History
-------

 * 1.0.1 fix bugs, docs, speed
 * 1.0.0 remove backward compatibility


"""
from __future__ import print_function, unicode_literals, division

__version__ = '1.0.1'
__author__ = __author_email__ = 'chrono-meter@gmx.net'
__license__ = 'PSF'
__url__ = 'http://pypi.python.org/pypi/katagami'
# http://pypi.python.org/pypi?%3Aaction=list_classifiers
__classifiers__ = [i.strip() for i in '''\
    Development Status :: 4 - Beta
    Intended Audience :: Developers
    License :: OSI Approved :: Python Software Foundation License
    Operating System :: OS Independent
    Programming Language :: Python :: 2.7
    Programming Language :: Python :: 3
    Topic :: Internet :: WWW/HTTP :: Dynamic Content :: CGI Tools/Libraries
    Topic :: Software Development :: Libraries :: Python Modules
    Topic :: Text Processing :: Markup :: HTML
    Topic :: Text Processing :: Markup :: XML
    '''.splitlines() if i.strip()]
    #Development Status :: 5 - Production/Stable

import sys
import re
import io
import tokenize
import logging; logger = logging.getLogger(__name__)
try:
    from functools import lru_cache
except ImportError:
    lru_cache = lambda *a, **k: lambda f: f
__all__ = ()
TAB = '    '


if sys.version < '2.7':
    raise RuntimeError('not supported version: %s' % sys.version)
# doctest compatibility with Python 2 and Python 3
if sys.version < '3':
    __doc__ = re.sub(
        "Can't convert '(.*?)' object to str implicitly",
        "coercing to Unicode: need string or buffer, \\1 found",
        __doc__)


def decorate_attributes(**kwargs):
    """convinient funcion attributes decorator"""
    def result(function):
        for i in kwargs.items():
            setattr(function, *i)
        return function
    return result


def get_xmlencoding(bytes, default='utf-8'):
    """search xml/html encoding and return"""
    encoding_patterns = (
        # <?xml encoding="utf-8"?>
        (b'<\?xml\\s+.*?encoding="([^"]+)".*?\?>', ),
        (b'<\?xml\\s+.*?encoding=\'([^\']+)\'.*?\?>', ),
        (b'<\?xml\\s+.*?encoding=(\\S+).*?\?>', ),
        # <meta charset="UTF-8">
        (b'<meta\\s+.*?charset="([^"]+)".*?>', ),
        (b'<meta\\s+.*?charset=\'([^\'])\'.*?>', ),
        (b'<meta\\s+.*?charset=(\\S+).*?>', ),
        # <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
        (b'<meta\\s+.*?http-equiv="Content-Type".*?>',
         b'content=".*?;\s*charset=([^"]+)"',
         ),
        (b'<meta\\s+.*?http-equiv=\'Content-Type\'.*?>',
         b'content=\'.*?;\s*charset=([^\']+)\'',
         ),
        (b'<meta\\s+.*?http-equiv=Content-Type.*?>',
         b'content=.*?;charset=(\\S+)',
         ),
        )
    for pattern in encoding_patterns:
        s = bytes
        match = None
        for i in pattern:
            match = re.search(i, s, re.DOTALL | re.IGNORECASE)
            if not match:
                break
            s = match.group(0)
        if match and match.group(1):
            return match.group(1).decode()

    return default


def set_pyindent(source, indent=''):
    tokens = []
    first_indent = None

    for token in tokenize.generate_tokens(io.StringIO(source).readline):
        if token[0] == tokenize.COMMENT:
            continue

        if first_indent is None and token[0] == tokenize.INDENT:
            first_indent = token[1]

        if first_indent and token[0] == tokenize.INDENT:
            token = token[0], re.subn('^' + first_indent, indent, token[1], 1)[0]
        else:
            token = token[:2]

        tokens.append(token)

    if not first_indent:
        tokens.insert(0, (tokenize.INDENT, indent))

    return tokenize.untokenize(tokens)


class Translator(object):

    if sys.version < '3':
        expr_concat_str = '__result__.append(%s)'
    else:
        expr_concat_str = '__result__ += %s'

    @lru_cache()
    def _translate(self, file, encoding=None):
        context = {
            '__file__': '<string>',
            '__encoding__': 'utf-8',
            '__code__': None,
            '__render__': self.render,
            }
        try:
            context['__str__'] = unicode
        except NameError:
            context['__str__'] = str

        # read content as bytes
        if hasattr(file, 'read'):
            content = file.read()
            context['__file__'] = getattr(file, 'name', '<string>')
        else:
            with open(file, 'rb') as fp:
                content = fp.read()
            context['__file__'] = file

        # detect encoding
        context['__encoding__'] = get_xmlencoding(content)

        # convert to unicode
        content = content.decode(context['__encoding__'])
        current = 0

        context['lines'] = []
        context['indent'] = 0
        context['feature'] = {}
        for match in re.finditer('<\?.*?\?>', content, re.DOTALL):
            # lineno = len(re.findall('(\r\n|\r|\n)', content[:match.start()])) + 1
            start, end = match.span()
            chunk = content[current:start]
            if chunk:
                context['lines'].append(
                    TAB * context['indent'] + self.expr_concat_str % repr(chunk))
            current = end

            chunk = match.group(0)[2:-2]

            for i in sorted(i for i in dir(self) if i.startswith('_handle_')):
                handler = getattr(self, i)
                if re.match(handler.pattern, chunk):
                    handler(context, chunk)
                    break

            # not supported <?...?>
            else:
                chunk = '<?%s?>' % chunk
                context['lines'].append(
                    TAB * context['indent'] + self.expr_concat_str % repr(chunk))

        assert context['indent'] == 0, \
               'Some indentation is remaining: %d' % context['indent']

        chunk = content[current:]
        if chunk:
            context['lines'].append(
                TAB * context['indent'] + self.expr_concat_str % repr(chunk))

        context['__script__'] = '\n'.join(context['lines'])
        logger.debug('template "%s" is translated: %s', context['__script__'],
                     context['__file__'])
        try:
            context['__code__'] = \
                compile(context['__script__'], context['__file__'], 'exec')
        except Exception as e:
            logger.exception(
                '%s\n%s', context['__file__'], context['__script__'])
            raise

        # cleanup
        for i in list(context):
            if not re.match('__.*?__', i):
                del context[i]

        return context

    # <?=...?>
    @decorate_attributes(pattern='^=')
    def _handle_inline_expression(self, context, chunk):
        chunk = chunk[1:].strip()

        # <?=context['feature'] cast_string="" trap_exceptions=""?>
        if re.match('feature\s+', chunk):
            context['feature'].clear()
            for i in re.finditer('(\S+)\s*=\s*"([^"]*)"', chunk,
                                 re.DOTALL):
                context['feature'][i.group(1)] = i.group(2).strip()

        # Python expression
        else:
            if context['feature'].get('cast_string') in ('True', 'true'):
                chunk = '__str__(%s)' % set_pyindent(chunk)
                # print(chunk, file=sys.stderr)
            if context['feature'].get('trap_exceptions') in ('True', 'true'):
                context['lines'].append(TAB * context['indent'] +
                    'try: ' + self.expr_concat_str % chunk)
                context['lines'].append(TAB * context['indent'] +
                    'except Exception as e: ' +
                    self.expr_concat_str % '__str__(e)')
            else:
                context['lines'].append(
                    TAB * context['indent'] + self.expr_concat_str % chunk)

    # <?py...?>
    @decorate_attributes(pattern='^py')
    def _handle_embed_script(self, context, chunk):
        chunk = chunk[2:]
        chunk = set_pyindent(chunk, TAB * context['indent'])
        context['lines'].append(chunk)

    # <?}...{?>
    @decorate_attributes(pattern='(^}|.*{$)')
    def _handle_indent(self, context, chunk):
        if chunk.startswith('}'):
            chunk = chunk[1:]
            context['indent'] -= 1
            assert context['indent'] >= 0, ''
        current_indent = context['indent']
        if chunk.endswith('{'):
            chunk = chunk[:-1]
            context['indent'] += 1

        chunk = chunk.strip()
        if chunk:
            context['lines'].append(TAB * current_indent + chunk)

    # <?\...?>
    @decorate_attributes(pattern='^\\\\')
    def _handle_escape(self, context, chunk):
        chunk = '<?%s?>' % chunk[1:]
        context['lines'].append(
            TAB * context['indent'] + self.expr_concat_str % repr(chunk))

    def translate(self, file, encoding=None):
        """translate template to Python script and return function"""
        context = self._translate(file, encoding)
        return lambda **locals: _surrogate_renderer(context, locals)

    def render(self, __file__, __encoding__=None, **locals):
        """render template with `locals` namespace values"""
        return self.translate(__file__, __encoding__)(**locals)

    def purge(self):
        """purge template caches"""
        if hasattr(self._translate, 'cache_clear'):
            self._translate.cache_clear()


def _surrogate_renderer(context, locals):
    """This function resolves this problem in Python 2::
        SyntaxError: unqualified exec is not allowed in function it is a nested function
    """
    _ = {}
    _.update(context)
    _.update(locals)
    if sys.version < '3':
        _['__result__'] = []
        exec(context['__code__'], _)
        return unicode.join('', _['__result__']).encode(context['__encoding__'])
    else:
        _['__result__'] = ''
        exec(context['__code__'], _)
        return _['__result__'].encode(context['__encoding__'])


def render(__file__, __encoding__=None, **locals):
    """render template with `locals` namespace values"""
    return translator.render(__file__, __encoding__, **locals)


translator = Translator()


if __name__ == '__main__':
    import __main__
    import os
    import doctest
    import distutils.core

    __main__.__name__ = os.path.splitext(os.path.basename(__file__))[0]
    target = __main__

    if 'check' in sys.argv:
        doctest.testmod(target)
        try:
            import docutils.core
        except ImportError:
            pass
        else:
            s = docutils.core.publish_string(target.__doc__, writer_name='html')
            with open(os.path.splitext(__file__)[0] + '.html', 'wb') as fp:
                fp.write(s)

    # http://docs.python.org/3/distutils/apiref.html?highlight=setup#distutils.core.setup
    distutils.core.setup(
        name=target.__name__,
        version=target.__version__,
        description=target.__doc__.splitlines()[0],
        long_description=target.__doc__,
        author=target.__author__,
        author_email=target.__author_email__,
        url=target.__url__,
        classifiers=target.__classifiers__,
        license=target.__license__,
        py_modules=[target.__name__, ],
        )


