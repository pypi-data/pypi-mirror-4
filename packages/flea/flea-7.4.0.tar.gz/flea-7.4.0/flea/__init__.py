from __future__ import print_function
import logging
import sys
import os
import re
import webbrowser

from io import BytesIO, StringIO
import wsgiref.validate
from wsgiref.simple_server import make_server
try:
    from http.cookies import BaseCookie
    from urllib.parse import unquote, urlparse, urlunparse
except ImportError:
    from Cookie import BaseCookie  # NOQA
    from urlparse import urlparse, urlunparse  # NOQA
    from urllib import unquote  # NOQA

from functools import wraps
from itertools import chain
from shutil import copyfileobj
from tempfile import NamedTemporaryFile

from lxml.html import fromstring, tostring
from lxml.cssselect import CSSSelector, SelectorSyntaxError
from lxml.etree import XPath, XPathError

from fresco import Request, Response
from fresco.util.urls import url_join, make_query
from fresco.util.http import parse_header
from fresco.util.wsgi import unicode_to_environ

#: Registry for xpath multimethods
xpath_registry = {}

#: EXSLT regular expression namespace URI
REGEXP_NAMESPACE = "http://exslt.org/regular-expressions"


if sys.version_info > (3, 0):
    PY3 = True
    string_types = str
else:
    PY3 = False
    string_types = (unicode, str)


class BadStatusError(AssertionError):
    """
    Raised when a non-success HTTP response is found (eg 404 or 500)
    """


class NotARedirectError(AssertionError):
    """
    Raised when an attempt is made to call follow() on a non-redirected
    response
    """


class XPathMultiMethod(object):
    """
    A callable object that has different implementations selected by XPath
    expressions.
    """

    def __init__(self):
        self.__doc__ = ''
        self.__name__ = ''
        self.endpoints = []

    def __call__(self, *args, **kwargs):
        el = args[0]
        el = getattr(el, 'el', el)
        for xpath, func in self.endpoints:
            if el in xpath(el):
                return func(*args, **kwargs)
        raise NotImplementedError("Function %s not implemented for element %r"\
                                  % (self.__name__, el,))

    def register(self, xpath, func):
        self.endpoints.append((
            XPath('|'.join('../%s' % item for item in xpath.split('|'))),
            func
        ))
        func_doc = getattr(func, '__doc__', getattr(func, 'func_doc', None))
        if not func_doc:
            return

        # Add wrapped function to the object's docstring
        # Note that ".. comment block" is required to fool rst/sphinx into
        # correctly parsing the indented paragraphs when there is only one
        # registered endpoint.
        doc = 'For elements matching ``%s``:'\
              '\n%s\n\n.. comment block\n\n' % (
                    xpath,
                    '\n'.join('    %s' % line
                              for line in func_doc.split('\n'))
        )
        self.__doc__ += doc
        self.__name__ = func.__name__


def when(xpath_expr):
    """
    Decorator for methods having different implementations selected by XPath
    expressions.
    """
    def when(func):
        if getattr(func, '__wrapped__', None):
            func = getattr(func, '__wrapped__')
        multimethod = xpath_registry.setdefault(func.__name__,
                                                XPathMultiMethod())
        multimethod.register(xpath_expr, func)
        wrapped = wraps(func)(
            lambda self, *args, **kwargs: multimethod(self, *args, **kwargs)
        )
        wrapped.__wrapped__ = func
        wrapped.func_doc = multimethod.__doc__
        wrapped.__doc__ = multimethod.__doc__
        return wrapped
    return when


class ElementWrapper(object):
    r"""
    Wrapper for an ``lxml.etree`` element, providing additional methods useful
    for driving/testing WSGI applications. ``ElementWrapper`` objects are
    normally created through the ``find``/``css`` methods of ``TestAgent``
    instance::

        >>> from fresco import Response
        >>> myapp = Response(['<html><body><a href="/">link 1</a>'\
        ...                   '<a href="/">link 2</a></body></html>'])
        >>> agent = TestAgent(myapp).get('/')
        >>> elementwrapper = agent.find('//a')[0]

    ``ElementWrapper`` objects have many methods and properties implemented as
    ``XPathMultiMethod`` objects, meaning their behaviour varies depending on
    the type of element being wrapped. For example, form elements have a
    ``submit`` method, ``a`` elements have a ``click`` method, and ``input``
    elements have a value property.
    """

    def __init__(self, agent, el):
        self.agent = agent
        self.el = el

    def __str__(self):

        if (len(self.el) == 0 and self.el.text is None):
            return self.html()

        return '<%s%s>...</%s>' % (
            self.el.tag,
            ''.join(' %s="%s"' % (key, escapeattrib(value))
                    for key, value in self.el.attrib.items()),
            self.el.tag,
        )

    __repr__ = __str__

    def __eq__(self, other):
        if self.__class__ is not other.__class__:
            return False
        return (
            self.el is other.el
            and self.agent is other.agent
        )

    def __getattr__(self, attr):
        return getattr(self.el, attr)

    def __call__(self, path, flavor='auto', **kwargs):
        if flavor == 'auto':
            flavor = guess_expression_flavor(path)

        if flavor == 'css':
            return self.css(path, **kwargs)
        else:
            return self.find(path, **kwargs)

    def find(self, path, namespaces=None, **kwargs):
        """
        Return elements matching the given xpath expression.

        If the xpath selects a list of elements a ``ResultWrapper`` object is
        returned.

        If the xpath selects any other type (eg a string attribute value), the
        result of the query is returned directly.

        For convenience that the EXSLT regular expression namespace
        (``http://exslt.org/regular-expressions``) is prebound to
        the prefix ``re``.
        """
        ns = {'re': REGEXP_NAMESPACE}
        if namespaces is not None:
            ns.update(namespaces)
        namespaces = ns

        result = self.el.xpath(path, namespaces=namespaces, **kwargs)

        if not isinstance(result, list):
            return result

        return ResultWrapper(
            (ElementWrapper(self.agent, el) for el in result),
            'xpath:' + path
        )

    def css(self, selector):
        """
        Return elements matching the given CSS Selector (see
        ``lxml.cssselect`` for documentation on the ``CSSSelector`` class.
        """
        compiled = CSSSelector(selector)
        return ResultWrapper(
            (ElementWrapper(self.agent, el) for el in compiled(self.el)),
            'css:' + selector
        )

    def __getitem__(self, path):
        result = self.find(path)
        if len(result) == 0:
            raise ValueError("%r matched no elements" % path)
        return result

    @when("a[@href]")  # NOQA
    def click(self, follow=True, check_status=True):
        """
        Follow a link and return a new instance of ``TestAgent``
        """
        return self.agent._click(self, follow=follow,
                                 check_status=check_status)

    @when("input[@type='submit' or @type='image']|button[@type='submit' or not(@type)]")  # NOQA
    def click(self, follow=True, check_status=True):
        """
        Alias for submit
        """
        return self.submit(follow, check_status=check_status)

    @when("input[@type='file']")  # NOQA
    def _set_value(self, value):
        """
        Set the value of the file upload, which must be a tuple of::

            (filename, content-type, data)

        Where data can either be a byte string or file-like object.
        """
        filename, content_type, data = value
        self.agent.file_uploads[self.el] = (filename, content_type, data)

        # Set the value in the DOM to the filename so that it can be seen when
        # the DOM is displayed
        self.el.attrib['value'] = filename

    @when("input[@type='file']")  # NOQA
    def _get_value(self):
        """
        Return the value of the file upload, which will be a tuple of
        ``(filename, content-type, data)``
        """
        return self.agent.file_uploads.get(self.el)

    @when("input|button")  # NOQA
    def _get_value(self):
        """
        Return the value of the input or button element
        """
        return self.el.attrib.get('value', '')

    @when("input|button")  # NOQA
    def _set_value(self, value):
        """
        Set the value of the input or button element
        """
        self.el.attrib['value'] = value

    value = property(_get_value, _set_value)

    @when("textarea|input|select")  # NOQA
    def input_group(self):
        """
        Return the group of inputs sharing the same name attribute
        """
        return self.form.find(
            """.//*[
                (local-name() = 'input'
                    or local-name() = 'textarea'
                    or local-name() = 'select')
                and (@name='{fieldname}')
            ]
            """.format(fieldname=self.attrib['name'])
        )

    @when("input[@type='checkbox']")  # NOQA
    def submit_value(self):
        """
        Return the value of the selected checkbox element as the user
        agent would return it to the server in a form submission.
        """
        if 'disabled' in self.el.attrib:
            return None
        if 'checked' in self.el.attrib:
            return self.el.attrib.get('value', 'On')
        return None

    @when("input[@type='radio']")  # NOQA
    def submit_value(self):
        """
        Return the value of the selected radio element as the user
        agent would return it to the server in a form submission.
        """
        if 'disabled' in self.el.attrib:
            return None
        if 'checked' in self.el.attrib:
            return self.el.attrib.get('value', '')
        return None

    @when("select[@multiple]")  # NOQA
    def submit_value(self):
        """
        Return the value of the selected radio/checkbox element as the user
        agent would return it to the server in a form submission.
        """
        if 'disabled' in self.el.attrib:
            return None
        return [item.attrib.get('value', item.text)
                for item in self.el.xpath('./option[@selected]')]

    @when("select[not(@multiple)]")  # NOQA
    def submit_value(self):
        """
        Return the value of the selected radio/checkbox element as the user
        agent would return it to the server in a form submission.
        """
        if 'disabled' in self.el.attrib:
            return None
        try:
            item = self.el.xpath('./option[@selected]')[0]
        except IndexError:
            try:
                item = self.el.xpath('./option[1]')[0]
            except IndexError:
                return None
        return item.attrib.get('value', item.text)

    @when("input[not(@type) or @type != 'submit' and @type != 'image' and @type != 'reset']")  # NOQA
    def submit_value(self):
        """
        Return the value of any other input element as the user
        agent would return it to the server in a form submission.
        """
        if 'disabled' in self.el.attrib:
            return None
        return self.value

    @when("input[@type != 'submit' or @type != 'image' or @type != 'reset']")  # NOQA
    def submit_value(self):
        """
        Return the value of any submit/reset input element
        """
        return None

    @when("textarea")  # NOQA
    def submit_value(self):
        """
        Return the value of any submit/reset input element
        """
        return self.el.text

    submit_value = property(submit_value)

    def _get_checked(self):
        """
        Return True if the element has the checked attribute
        """
        return 'checked' in self.el.attrib

    @when("input[@type='radio']")  # NOQA
    def _set_checked(self, value):
        """
        Set the radio button state to checked (unchecking any others in the
        group)
        """
        for el in self.el.xpath(
            "./ancestor-or-self::form[1]"\
            "//input[@type='radio' and @name=$name]",
            name=self.el.attrib.get('name', '')
        ):
            if 'checked' in el.attrib:
                del el.attrib['checked']

        if bool(value):
            self.el.attrib['checked'] = 'checked'
        else:
            if 'checked' in self.el.attrib:
                del self.el.attrib['checked']

    @when("input")  # NOQA
    def _set_checked(self, value):
        """
        Set the (checkbox) input state to checked
        """
        if bool(value):
            self.el.attrib['checked'] = 'checked'
        else:
            try:
                del self.el.attrib['checked']
            except KeyError:
                pass
    checked = property(_get_checked, _set_checked)

    @when("option")  # NOQA
    def _get_selected(self, value):
        """
        Return True if the given select option is selected
        """
        return 'selected' in self.el.attrib

    @when("option")  # NOQA
    def _set_selected(self, value):
        """
        Set the ``selected`` attribute for the select option element. If the
        select does not have the ``multiple`` attribute, unselect any
        previously selected option.
        """
        if 'multiple' not in \
           self.el.xpath('./ancestor-or-self::select[1]')[0].attrib:
            for el in \
            self.el.xpath("./ancestor-or-self::select[1]//option"):
                if 'selected' in el.attrib:
                    del el.attrib['selected']

        if bool(value):
            self.el.attrib['selected'] = ''
        else:
            if 'selected' in self.el.attrib:
                del self.el.attrib['selected']

    selected = property(_get_selected, _set_selected)

    @property  # NOQA
    @when("input|textarea|button|select|form")
    def form(self):
        """
        Return the form associated with the wrapped element.
        """
        return self.__class__(
            self.agent,
            self.el.xpath("./ancestor-or-self::form[1]")[0]
        )

    @when("input[@type='submit' or @type='image']|button[@type='submit' or not(@type)]")  # NOQA
    def submit(self, follow=True, check_status=True):
        """
        Submit the form, returning a new ``TestAgent`` object, by clicking on
        the selected submit element (input of
        type submit or image, or button with type submit)
        """
        return self.form.submit(self, follow=follow, check_status=check_status)

    @when("form")  # NOQA
    def submit(self, button=None, follow=True, check_status=True):
        """
        Submit the form, returning a new ``TestAgent`` object
        """
        method = self.el.attrib.get('method', 'GET').upper()
        data = self.submit_data(button)
        path = url_join_same_server(
            self.agent.request.url,
            self.el.attrib.get('action', self.agent.request.path)
        )
        return {
            ('GET', None): self.agent.get,
            ('POST', None): self.agent.post,
            ('POST', 'application/x-www-form-urlencoded'): self.agent.post,
            ('POST', 'multipart/form-data'): self.agent.post_multipart,
        }[(method, self.el.attrib.get('enctype'))](path, data,
                                                   follow=follow,
                                                   check_status=check_status)

    @when("input[@type='submit' or @type='image']|button[@type='submit' or not(@type)]")  # NOQA
    def submit_data(self):
        """
        Return a list of the data that would be submitted to the server
        in the format ``[(key, value), ...]``, without actually submitting the
        form.
        """
        return self.form.submit_data(self)

    @when("form")  # NOQA
    def submit_data(self, button=None):
        """
        Return a list of the data that would be submitted to the server
        in the format ``[(key, value), ...]``, without actually submitting the
        form.
        """
        data = []
        if isinstance(button, string_types):
            button = self(button)

        if button and 'name' in button.attrib:
            data.append((button.attrib['name'], button.value))
            if button.el.attrib.get('type') == 'image':
                data.append((button.attrib['name'] + '.x', '1'))
                data.append((button.attrib['name'] + '.y', '1'))

        inputs = (ElementWrapper(self.agent, el)
                  for el in self.el.xpath('.//input|.//textarea|.//select'))
        for input in inputs:
            try:
                name = input.attrib['name']
            except KeyError:
                continue
            value = input.submit_value
            if value is None:
                continue

            elif input.attrib.get('type') == 'file' \
                    and isinstance(value, tuple):
                data.append((name, value))

            elif isinstance(value, string_types):
                data.append((name, value))

            else:
                data += [(name, v) for v in value]

        return data

    @when("form")  # NOQA
    def fill(self, *args, **kwargs):
        """
        Fill the current form with data.

        :param \*args: Pairs of ``(selector, value)``

        :param \*\*kwargs: mappings of fieldname to value

        See the documentation for :meth:`_set_value` implementations
        for individual form control types to see how values are processed
        as this varies between text inputs, selects, radio buttons,
        checkboxes etc
        """

        for selector, value in args:
            self(selector).fill(value)

        for name, value in kwargs.items():
            path = """
            .//*[
                (local-name() = 'input'\
                 or local-name() = 'textarea'\
                 or local-name() = 'select')
                and (@name=$name or @id=$name)
            ]"""
            self.find(path, name=name).fill(value)

        return self

    @when("input[@type='checkbox']")  # NOQA
    def fill(self, values):

        if values is None:
            values = []

        if isinstance(values, bool):
            self.checked = values

        elif values and all(isinstance(v, bool) for v in values):
            # List of bools, eg ``[True, False, True]``
            for el, checked in zip(self.input_group(), values):
                if checked:
                    el.attrib["checked"] = ""
                elif 'checked' in el.attrib:
                    del el.attrib['checked']

        else:
            # List of values, eg ``['1', '23', '8']``
            found = set()
            values = set(str(v) for v in values)
            for el in self.input_group():
                if el.attrib.get('value') in values:
                    el.attrib['checked'] = ""
                    found.add(el.attrib['value'])
                elif 'checked' in el.attrib:
                    del el.attrib['checked']
            if found != values:
                raise AssertionError("Values %r not present"\
                                     " in checkbox group %r" %\
                                     (values - found,
                                      self.el.attrib.get('name')))

        return self

    @when("input[@type='radio']")  # NOQA
    def fill(self, value):
        """
        Set the value of the radio button, by searching for the radio
        button in the group with the given value and checking it.
        """
        if value is not None:
            value = str(value)
        found = False
        for el in self.el.xpath(
            "./ancestor-or-self::form[1]//input[@type='radio' and @name=$n]",
            n=self.el.attrib.get('name', '')
        ):
            if (el.attrib.get('value') == value):
                el.attrib['checked'] = ""
                found = True
            elif 'checked' in el.attrib:
                del el.attrib['checked']
        if value is not None and not found:
            raise AssertionError("Value %r not present"\
                                 " in radio button group %r" %\
                                 (value, self.el.attrib.get('name')))
        return self

    @when("textarea")  # NOQA
    def fill(self, value):
        """
        Set the value of a textarea control
        """
        if value is not None:
            value = str(value)
        self.el.text = value
        return self

    @when("input[@type='file']")  # NOQA
    def fill(self, value):
        """
        Set the value of a file input box
        """
        if value is None:
            try:
                del self.el.attrib['value']
            except KeyError:
                pass
        else:
            self.value = value
        return self

    @when("input")  # NOQA
    def fill(self, value):
        """
        Set the value of a (text, password, ...) input box
        """
        if value is None:
            try:
                del self.el.attrib['value']
            except KeyError:
                pass
        else:
            self.value = str(value)
        return self

    @when("select[@multiple]")  # NOQA
    def fill(self, values):
        """
        Set the values of a multiple select box

        :param values: list of values to be selected
        """
        options = self.el.xpath('.//option')
        if all(isinstance(v, bool) for v in values):
            values = [
                opt.attrib.get('value', opt.text)
                for selected, opt in zip(values, options)
            ]

        found = set()
        values = set(str(v) for v in values)
        for opt in options:
            value = opt.attrib.get('value', opt.text)
            if value in values:
                opt.attrib['selected'] = ""
                found.add(value)
            elif 'selected' in opt.attrib:
                del opt.attrib['selected']
        if found != values:
            raise AssertionError("Values %r not present in select %r" % (
                values - found,
                self.el.attrib.get('name'))
            )
        return self

    @when("select[not(@multiple)]")  # NOQA
    def fill(self, value):
        """
        Set the values of a multiple select box

        :param values: list of values to be selected
        """
        if value is not None:
            value = str(value)
        found = False
        for opt in self.el.xpath('.//option'):
            if opt.attrib.get('value', opt.text) == value:
                opt.attrib['selected'] = ""
                found = True
            elif 'selected' in opt.attrib:
                del opt.attrib['selected']
        if not found and value is not None:
            raise AssertionError("Value %r not present in select %r" %\
                                 (value, self.el.attrib.get('name')))
        return self

    def html(self):
        """
        Return an HTML representation of the element

        :rtype: unicode string
        """
        return tostring(self.el, encoding='unicode')

    def pretty(self):
        """
        Return an pretty-printed string representation of the element

        :rtype: unicode string
        """
        return tostring(self.el, encoding='unicode', pretty_print=True)

    def striptags(self):
        r"""
        Strip tags out of the element and its children to leave only the
        textual content. Normalize all sequences of whitespace to a single
        space.

        Use this for simple text comparisons when testing for document content

        Example::

            >>> from fresco import Response
            >>> myapp = Response(['<p>the <span>foo</span> is'\
            ...                   ' completely <strong>b</strong>azzed</p>'])
            >>> agent = TestAgent(myapp).get('/')
            >>> agent['//p'].striptags()
            'the foo is completely bazzed'

        """
        def _striptags(node):
            if node.text:
                yield node.text
            for subnode in node:
                for text in _striptags(subnode):
                    yield text
                if subnode.tail:
                    yield subnode.tail
        return re.sub(r'\s\s*', ' ', ''.join(_striptags(self.el)))

    def __contains__(self, what):
        return what in self.html()


class ResultWrapper(list):
    """
    Wrap a list of elements (``ElementWrapper`` objects) returned from an xpath
    query, providing reasonable default behaviour for testing.

    ``ResultWrapper`` objects usually wrap ``ElementWrapper`` objects, which in
    turn wrap an lxml element and are normally created through the find/findcss
    methods of ``TestAgent``::

        >>> from fresco import Response
        >>> myapp = Response(['<html><p>item 1</p><p>item 2</p></html>'])
        >>> agent = TestAgent(myapp).get('/')
        >>> resultwrapper = agent.find('//p')

    ``ResultWrapper`` objects have list like behaviour::

        >>> len(resultwrapper)
        2
        >>> resultwrapper[0] #doctest: +ELLIPSIS
        <p>...</p>

    Attributes that are not part of the list interface are proxied to the first
    item in the result list for convenience. These two uses are equivalent::

        >>> resultwrapper[0].text
        'item 1'
        >>> resultwrapper.text
        'item 1'

    Items in the ``ResultWrapper`` are ``ElementWrapper`` instances, which
    provide methods in addition to the normal lxml.element methods (eg
    ``click()``, setting/getting form field values etc).

    """
    def __init__(self, elements, expr=None):
        super(ResultWrapper, self).__init__(elements)
        self.__dict__['expr'] = expr

    def __getattr__(self, attr):
        return getattr(self[0], attr)

    def __setattr__(self, attr, value):
        return setattr(self[0], attr, value)

    def __getitem__(self, item):
        try:
            if isinstance(item, int):
                return super(ResultWrapper, self).__getitem__(item)
            else:
                return self[0][item]
        except IndexError:
            raise IndexError("list index out of range for %r" % (self,))

    def __contains__(self, what):
        return self[0].__contains__(what)

    def __repr__(self):
        return "<ResultWrapper %r>" % (self.__dict__['expr'],)

    def filter_on_text(self, matcher):
        """
        Return a new :class:`ResultWrapper` of the elements in ``elements``
        where applying the function ``matcher`` to the text contained in
        the element results in a truth value.
        """
        return self.__class__(
            (e for e in self if matcher(e.striptags())),
            self.expr + " (filtered by %s)" % (matcher)
        )

    def filter(self, matcher):
        """
        Return a new :class:`ResultWrapper` of the elements in ``elements``
        where applying the function ``matcher`` to the element results in
        a truth value. """
        return self.__class__(
            (e for e in self if matcher(e)),
            self.expr + " (filtered by %s)" % (matcher)
        )


class TestAgent(object):
    """
    A ``TestAgent`` object provides a user agent for the WSGI application under
    test.

    Key methods and properties:

        - ``get(path)``, ``post(path)``, ``post_multipart`` - create get/post
          requests for the WSGI application and return a new ``TestAgent``
          object

        - ``request``, ``response`` - the `Fresco <http://fresco.redgecko.org/>`_
          request and response objects associated with the last WSGI request.

        - ``body`` - the body response as a bytes object

        - ``body_decoded`` - the body response decoded into a string

        - ``lxml`` - the lxml representation of the response body (only
           applicable for HTML responses)

        - ``reset()`` - reset the TestAgent object to its initial state,
           discarding any form field values

        - ``find()`` (or dictionary-style attribute access) - evalute the given
           xpath expression against the current response body and return a
           ``ResultWrapper`` object.
    """

    response_class = Response

    default_charset = 'UTF-8'

    _lxml = None
    _body = None

    environ_defaults = {
        'SCRIPT_NAME': "",
        'PATH_INFO': "",
        'QUERY_STRING': "",
        'SERVER_NAME': "localhost",
        'SERVER_PORT': "8080",
        'SERVER_PROTOCOL': "HTTP/1.0",
        'REMOTE_ADDR': '127.0.0.1',
        'wsgi.version': (1, 0),
        'wsgi.url_scheme': 'http',
        'wsgi.multithread': False,
        'wsgi.multiprocess': False,
        'wsgi.run_once': False,
        'flea.testing': True,
    }

    def __init__(self, app, request=None, response=None, cookies=None,
                 history=None, validate_wsgi=True, host='127.0.0.1',
                 port='8080', loglevel=None, logger=None, close_response=True):
        """
        Initialize the ``TestAgent`` object.

        :param app: The WSGI app under test
        :param validate_wsgi: If True, the application under test will be
                              wrapped in ``wsgiref.validate.validator``
                              middleware.
        :param host: The host to use for the WSGI environ ``SERVER_NAME`` key
        :param port: The port to use for the WSGI environ ``SERVER_PORT`` key
        :param loglevel: Controls logging verbosity, eg ``logging.DEBUG``
                         ``None`` means no logging
        :param logger: A ``logging.Logger`` object. If supplied ``loglevel``
                       will be ignored.
        :param close_response: If ``True`` the response iterator will be
                               read from and closed immediately. If
                               ``False``, it is up to the caller to handle
                               closing the WSGI iterator at the end of the
                               request.

        The following parameters are intended for internal use only:

        :param history: The history list
        :param cookie: The cookie store to use for the TestAgent.
        :param request: The ``fresco.request.Request`` object associated with
                        the current request
        :param response: The ``fresco.request.Response`` object associated with
                         the current request
        """

        if logger is not None:
            logger = logger
        elif loglevel is not None:
            logger = logging.getLogger(self.__class__.__name__)
            logger.setLevel(loglevel)
        else:
            logger = None

        self.options = {
            'host': host,
            'port': port,
            'validate_wsgi': validate_wsgi,
            'logger': logger,
            'close_response': close_response,
        }

        self.request = request
        self.response = response

        #: The original wsgi application
        self.app = app

        if self.options['validate_wsgi']:
            self.validated_app = wsgiref.validate.validator(app)
        else:
            self.validated_app = app

        if cookies:
            self.cookies = cookies
        else:
            self.cookies = BaseCookie()

        if history:
            self.history = history
        else:
            self.history = []

        if response:
            _, opts = parse_header(response.get_header('Content-Type'))
            self.charset = opts.get('charset', self.default_charset)
            self.cookies.update(parse_cookies(response))
            if self.options['close_response']:
                self._read_response()
        else:
            self.charset = self.default_charset

        # Stores file upload field values in forms
        self.file_uploads = {}

        self.environ_defaults = self.__class__.environ_defaults.copy()
        self.environ_defaults.update({'SERVER_NAME': host,
                                      'SERVER_PORT': str(port)})

    def make_environ(self, REQUEST_METHOD='GET', PATH_INFO='', wsgi_input=b'',
                     **kwargs):
        """
        Return a dictionary suitable for use as the WSGI environ.

        PATH_INFO must be URL encoded. As a convenience it may also contain a
        query string portion which will be used as the QUERY_STRING WSGI
        variable.
        """
        SCRIPT_NAME = kwargs.pop('SCRIPT_NAME',
                                 self.environ_defaults["SCRIPT_NAME"])

        if SCRIPT_NAME and SCRIPT_NAME[-1] == '/':
            SCRIPT_NAME = SCRIPT_NAME[:-1]
            PATH_INFO = '/' + PATH_INFO

        if '?' in PATH_INFO:
            if 'QUERY_STRING' in kwargs:
                raise AssertionError("QUERY_STRING specified both in "\
                                     "PATH_INFO and as argument to "\
                                     "make_environ")
            PATH_INFO, querystring = PATH_INFO.split('?', 1)
            kwargs['QUERY_STRING'] = unicode_to_environ(querystring)

        assert re.match(r'^[/A-Za-z0-9\-._~!$/&\'()*+,;=:@%]*$', PATH_INFO), \
            "Path info not URL encoded"

        assert not re.search(r'%(?![A-F0-9]{2})', PATH_INFO), \
            "Path info not URL encoded"

        PATH_INFO = unquote(PATH_INFO)
        SCRIPT_NAME = unquote(SCRIPT_NAME)
        PATH_INFO = unicode_to_environ(PATH_INFO)
        SCRIPT_NAME = unicode_to_environ(SCRIPT_NAME)

        environ = self.environ_defaults.copy()
        environ.update(kwargs)
        for key, value in kwargs.items():
            environ[key.replace('wsgi_', 'wsgi.')] = value
            if '.' not in key:
                value = unicode_to_environ(value)

        if isinstance(wsgi_input, bytes):
            wsgi_input = BytesIO(wsgi_input)

        environ.update({
            'REQUEST_METHOD': REQUEST_METHOD,
            'SCRIPT_NAME': SCRIPT_NAME,
            'PATH_INFO': PATH_INFO,
            'wsgi.input': wsgi_input,
            'wsgi.errors': StringIO(),
        })

        if environ['SCRIPT_NAME'] == '/':
            environ['SCRIPT_NAME'] = ''
            environ['PATH_INFO'] = '/' + environ['PATH_INFO']

        while PATH_INFO.startswith('//'):
            PATH_INFO = PATH_INFO[1:]

        return environ

    def _request(self, environ, follow=True, history=False, check_status=True):
        """
        Low level entry point for making requests to the WSGI application.

        Return a TestAgent object representing the new state resulting from the
        request.

        :param environ: WSGI environ to be used for the request

        :param follow: If false, redirect responses will not be followed

        :param history: If true, a new entry will be added to the history
                        attribute for the resulting TestAgent object

        :param check_status: If true, any non success HTTP status code will
                             result in an AssertionError being raised
        """
        path = environ['SCRIPT_NAME'] + environ['PATH_INFO']
        environ['HTTP_COOKIE'] = '; '.join(
            '%s=%s' % (key, morsel.value)
            for key, morsel in self.cookies.items()
            if path.startswith(morsel['path'])
        )

        if history:
            history = self.history + [self]
        else:
            history = self.history

        if self.options['logger']:
            self.options['logger'].info("%s %s", environ['REQUEST_METHOD'],
                                        Request(environ).url)
            if environ['HTTP_COOKIE']:
                self.options['logger'].debug("Cookie: %s",
                                             environ['HTTP_COOKIE'])
            postdata = environ['wsgi.input'].getvalue()
            environ['wsgi.input'].seek(0)
            if postdata:
                self.options['logger'].info("wsgi.input: %r", postdata)

        response = self.response_class.from_wsgi(self.validated_app, environ,
                                                 self.start_response)
        agent = self.__class__(
            self.app,
            Request(environ),
            response,
            self.cookies,
            history,
            **self.options
        )
        if self.options['logger']:
            self.options['logger'].info('Response: %s', response.status)
            for name, value in response.headers:
                self.options['logger'].debug('Response: %s: %s', name, value)

        if check_status and response.status[0] not in '23':
            raise BadStatusError("%s %r returned HTTP status %r" % (
                environ['REQUEST_METHOD'],
                path,
                response.status
            ))

        if follow:
            return agent.follow_all()
        return agent

    def get(self, PATH_INFO='/', data=None, charset='UTF-8', follow=True,
            history=True, check_status=True, **kwargs):
        """
        Make a GET request to the application and return the response.

        PATH_INFO
            The path to request from the application. This must be URL encoded.
            As a convenience, query string data can be appended to this.
            Example value: ``agent.get('/my%20script?param=1')``

        data
            Query string data to be appended to the request, must be either a
            dict or list of ``(name, value)`` tuples.

        charset
            Encoding used for any unicode values encountered in ``data``

        follow
            If false, redirect responses will not be followed

        history
            If true, a new entry will be added to the history attribute for the
            resulting TestAgent object

        check_status
            If true, any non success HTTP status code will result in an
            AssertionError being raised

        """
        if data is not None:
            kwargs.setdefault('QUERY_STRING', make_query(data,
                                                         charset=charset))

        if self.request:
            PATH_INFO = url_join_same_server(self.request.url,
                                             PATH_INFO)

        return self._request(
            self.make_environ(
                'GET',
                PATH_INFO,
                **kwargs
            ),
            follow,
            history,
            check_status,
        )

    def post(self, PATH_INFO='/', data=None, charset='UTF-8', follow=True,
             history=True, check_status=True, **kwargs):
        """
        Make a POST request to the application and return the response.

        PATH_INFO
            The path to request from the application. This must be URL encoded.

        data
            POST data to be sent to the application, must be either a
            dict or list of ``(name, value)`` tuples.

        charset
            Encoding used for any unicode values encountered in ``data``

        follow
            If false, redirect responses will not be followed

        history
            If true, a new entry will be added to the history attribute for the
            resulting TestAgent object

        check_status
            If true, any non success HTTP status code will result in an
            AssertionError being raised


        """
        if data is None:
            data = []

        if self.request:
            PATH_INFO = url_join_same_server(self.request.url,
                                             PATH_INFO)

        data = make_query(data, charset=charset).encode('ASCII')
        wsgi_input = BytesIO(data)
        wsgi_input.seek(0)

        return self._request(
            self.make_environ(
                'POST',
                PATH_INFO,
                CONTENT_TYPE="application/x-www-form-urlencoded",
                CONTENT_LENGTH=str(len(data)),
                wsgi_input=wsgi_input,
                **kwargs
            ),
            follow,
            history,
            check_status,
        )

    def post_multipart(self, PATH_INFO='/', data=None, files=None,
                       charset='UTF-8', follow=True, history=True,
                       check_status=True, **kwargs):
        """
        POST a request to the given URI using multipart/form-data encoding.

        PATH_INFO
            The path to request from the application. This must be a URL
            encoded string.

        data
            POST data to be sent to the application, must be either a
            dict or list of ``(name, value)`` tuples.

        files
            list of ``(name, filename, content_type, data)`` tuples. ``data``
            may be either a byte string, iterator or file-like object.

        history
            If true, a new entry will be added to the history attribute for the
            resulting TestAgent object

        check_status
            If true, any non success HTTP status code will result in an
            AssertionError being raised

        """

        if data is None:
            data = {}

        try:
            data = data.items()
        except AttributeError:
            pass

        if files is None:
            files = []

        if self.request:
            PATH_INFO = url_join_same_server(self.request.url,
                                             PATH_INFO)

        boundary = b'----------------------------------------BoUnDaRyVaLuE'

        def add_headers(key, value):
            """
            Return a tuple of ``([(header-name, header-value), ...], data)``
            for the given key/value pair
            """
            if isinstance(value, tuple):
                filename, content_type, data = value
                headers = [
                    ('Content-Disposition',
                     'form-data; name="%s"; filename="%s"' %
                            (key, filename)),
                    ('Content-Type', content_type)
                ]
                return headers, data
            else:
                if not isinstance(value, bytes):
                    value = value.encode(charset)
                headers = [
                    ('Content-Disposition',
                    'form-data; name="%s"' % (key,))
                ]
                return headers, value

        items = chain(
            (add_headers(k, v) for k, v in data),
            (add_headers(k, (fname, ctype, data))
             for k, fname, ctype, data in files),
        )

        CRLF = b'\r\n'
        post_data = BytesIO()
        post_data.write(b'--' + boundary)
        for headers, data in items:
            post_data.write(CRLF)
            for name, value in headers:
                line = '%s: %s' % (name, value)
                post_data.write(line.encode('ascii'))
                post_data.write(CRLF)
            post_data.write(CRLF)
            if hasattr(data, 'read'):
                copyfileobj(data, post_data)
            elif isinstance(data, bytes):
                post_data.write(data)
            elif isinstance(data, string_types):
                post_data.write(data.encode('ascii'))
            else:
                for chunk in data:
                    post_data.write(chunk)
            post_data.write(CRLF)
            post_data.write(b'--' + boundary)
        post_data.write(b'--' + CRLF)
        length = post_data.tell()
        post_data.seek(0)
        kwargs.setdefault('CONTENT_LENGTH', str(length))
        return self._request(
            self.make_environ(
                'POST',
                PATH_INFO,
                CONTENT_TYPE=unicode_to_environ(
                                'multipart/form-data; boundary=' +
                                boundary.decode('ascii')),
                wsgi_input=post_data,
                **kwargs
            ),
            follow=follow,
            history=history,
            check_status=check_status,
        )

    def reload(self, follow=True, check_status=True):
        """
        Reload the current page, if necessary re-posting any data.

        Form fields that have been filled in on the loaded page, they will be
        refilled on the reloaded page, provided that the reloaded page has
        exactly the same fields present in the same order.
        """
        self.options['logger'] and self.options['logger'].debug("Reload: %s",
                                          self.request.path)
        env = self.request.environ.copy()
        del env['fresco.request']

        wsgi_input = env['wsgi.input']
        if isinstance(wsgi_input, wsgiref.validate.InputWrapper):
            wsgi_input = wsgi_input.input
        wsgi_input.seek(0)
        env['wsgi.input'] = wsgi_input
        agent = self._request(env, follow=follow, check_status=check_status)

        for src, dst in zip(
            self.find('//input|//textarea|//option'),
            agent.find('//input|//textarea|//option')
        ):
            if not all([
                src.tag == dst.tag,
                src.attrib.get('name') == dst.attrib.get('name'),
                src.attrib.get('type') == dst.attrib.get('type'),
            ]):
                break

            if (
                src.tag == 'input'
                and src.attrib.get('type') in ('radio', 'checkbox')
            ):
                if 'checked' in src.attrib:
                    dst.attrib['checked'] = src.attrib['checked']
                elif 'checked' in dst.attrib:
                    del dst.attrib['checked']

            elif src.tag == 'option':
                if 'selected' in src.attrib:
                    dst.attrib['selected'] = src.attrib['selected']
                elif 'selected' in dst.attrib:
                    del dst.attrib['selected']

            elif src.tag == 'textarea':
                dst.el.text = src.el.text

            else:
                if 'value' in src.attrib:
                    dst.attrib['value'] = src.attrib['value']
                elif 'value' in dst.attrib:
                    del dst.attrib['value']

        return agent

    def start_response(self, status, headers, exc_info=None):
        """
        No-op implementation.
        """

    def __str__(self):
        if self.response:
            return str(self.response)
        else:
            return super(TestAgent, self).__str__()

    def _read_response(self):

        if not self.response:
            return
        if self._body is not None:
            return
        try:
            self._body = b''.join(self.response.content)
        finally:
            try:
                self.response.content.close()
            except AttributeError:
                pass

    @property
    def body_bytes(self):
        """
        The body of the response

        :rtype: bytes
        """
        if self._body is None:
            self._read_response()
        return self._body

    @property
    def body(self):
        if self.body_bytes is None:
            return None
        return self.body_bytes.decode(self.charset)

    @property
    def lxml(self):
        if self._lxml is not None:
            return self._lxml
        self.reset()
        return self._lxml

    @property
    def root_element(self):
        return ElementWrapper(self, self.lxml)

    def reset(self):
        """
        Reset the lxml document, abandoning any changes made
        """
        self._lxml = fromstring(self.body)

    def find(self, path, namespaces=None, **kwargs):
        """
        Return elements matching the given xpath expression.

        If the xpath selects a list of elements a ``ResultWrapper`` object is
        returned.

        If the xpath selects any other type (eg a string attribute value), the
        result of the query is returned directly.

        For convenience that the EXSLT regular expression namespace
        (``http://exslt.org/regular-expressions``) is prebound to
        the prefix ``re``.
        """
        return self.root_element.find(path, namespaces, **kwargs)

    def __call__(self, path, flavor='auto', **kwargs):
        return self.root_element(path, flavor, **kwargs)

    def __getitem__(self, path):
        return self.root_element[path]

    def css(self, selector):
        """
        Return elements matching the given CSS Selector (see
        ``lxml.cssselect`` for documentation on the ``CSSSelector`` class.
        """
        return self.root_element.css(selector)

    def click(self, linkspec, flavor='auto', ignorecase=True, index=0,
              follow=True, check_status=True, **kwargs):
        """
        Click the link matched by ``linkspec``. See :meth:`findlinks` for a
        description of the link finding parameters

        :param linkspec:   specification of the link to be clicked
        :param flavor:     if ``css``, ``linkspec`` must be a CSS selector,
                           which must returning one or more links; if
                           ``xpath``, ``linkspec`` must be an XPath expression
                           returning one or more links; any other value will be
                           passed to :meth:`findlinks`.
        :param ignorecase: (see :meth:`findlinks`)
        :param index:      index of the link to click in the case of multiple
                           matching links
        """
        if flavor == 'css':
            links = self.css(linkspec, **kwargs)
        elif flavor == 'xpath':
            links = self.find(linkspec, **kwargs)
        else:
            links = self.findlinks(linkspec, flavor, ignorecase, **kwargs)
        return links[index].click(follow=follow, check_status=check_status)

    def findlinks(self, linkspec, flavor='auto', ignorecase=True, **kwargs):
        """
        Return a :class:`ResultWrapper` of links matched by ``linkspec``.

        :param linkspec:   specification of the link to be clicked
        :param ignorecase: if ``True``, the link search will be case
                           insensitive
        :param flavor:     one of ``auto``, ``text``, ``contains``,
                         ``startswith``, ``re``

        The ``flavor`` parameter is interpreted according to the following
        rules:

        - if ``auto``: detect links based on the following criteria:

            - if ``linkspec`` is a regular expression or otherwise has a
                ``search`` method, this will be used to match links.

            - if ``linkspec`` is callable, each link will be tested
                against it in turn, and the first link that returns True
                will be selected.

            - otherwise ``contains`` matching will be used

        - if ``text``: for links where the text of the link is ``linkspec``
        - if ``contains``: for links where the link text contains ``linkspec``
        - if ``startswith``: for links where the link text contains
          ``linkspec``
        - if ``re``: for links where the text of the link matches ``linkspec``
        """

        links = self.find('//a')

        if flavor == 'auto':
            if callable(linkspec):
                return links.filter(linkspec)
            elif hasattr(linkspec, 'search') and callable(linkspec.search):
                return links.filter_on_text(linkspec.search)
            else:
                flavor = 'contains'

        if ignorecase and flavor in ('text', 'contains', 'startswith'):
            linkspec = linkspec.lower()
            normcase = lambda x: x.lower()
        else:
            normcase = lambda x: x

        if flavor == 'text':
            matcher = lambda text, l=linkspec: l == normcase(text)

        elif flavor == 'contains':
            matcher = lambda text, l=linkspec: l in normcase(text)

        elif flavor == 'startswith':
            matcher = lambda text, l=linkspec: normcase(text).startswith(l)

        elif flavor == 're':
            flags = re.I if ignorecase else 0
            matcher = re.compile(linkspec, flags).search

        else:
            raise AssertionError("bad flavor: " + flavor)

        return links.filter_on_text(matcher)

    def _click(self, el, follow=True, check_status=True):
        href = el.attrib['href']
        if '#' in href:
            href = href.split('#')[0]
        return self.get(href, follow=follow, check_status=check_status)

    def follow(self):
        """
        If response has a ``30x`` status code, fetch (``GET``) the redirect
        target. No entry is recorded in the agent's history list.
        """
        if not (300 <= int(self.response.status.split()[0]) < 400):
            raise NotARedirectError(
                "Can't follow non-redirect response (got %s for %s %s)" % (
                    self.response.status,
                    self.request.method,
                    self.request.path
                )
            )

        return self.get(
            self.response.get_header('Location'),
            history=False,
            follow=False,
        )

    def follow_all(self):
        """
        If response has a ``30x`` status code, fetch (``GET``) the redirect
        target, until a non-redirect code is received. No entries are recorded
        in the agent's history list.
        """

        agent = self
        while True:
            try:
                agent = agent.follow()
            except NotARedirectError:
                return agent

    def new_session(self):
        """
        Return a new TestAgent with all cookies deleted.
        This gives an easy way to test session expiry.
        """
        agent = self.__class__(
            self.app,
            self.request,
            self.response,
            None,
            self.history,
            **self.options
        )
        agent.cookies = BaseCookie()
        return agent

    def back(self, count=1):
        return self.history[-abs(count)]

    def showbrowser(self):
        """
        Open the current page in a web browser
        """
        tmp = NamedTemporaryFile(delete=False)
        tmp.write(tostring(self.lxml, encoding='utf8'))
        tmp.close()
        webbrowser.open_new_tab('file:' + tmp.name.replace(os.sep, '/'))

    def serve(self, open_in_browser=True):
        """
        Start a HTTP server for the application under test.

        The host/port used for the HTTP server is determined by the ``host``
        and ``port`` arguments to the ``TestAgent`` constructor.

        The initial page rendered to the browser will the currently loaded
        document (in its current state - so if changes have been made, eg form
        fields filled these will be present in the HTML served to the browser).
        Any cookies the TestAgent has stored are also forwarded to the browser.

        Subsequent requests from the browser are then proxied directly to the
        WSGI application under test.
        """
        host = self.environ_defaults['SERVER_NAME']
        port = int(self.environ_defaults['SERVER_PORT'])

        server = make_server(host, port, PassStateWSGIApp(self))
        url = self.request.make_uri(netloc='{0}:{1}'.format(host, port))
        if open_in_browser:
            webbrowser.open_new_tab(url)
        print("\nStarting HTTP server on {0}:{1}. "
              "Press ctrl-c to exit.".format(host, port))
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass

    def __enter__(self):
        """
        Provde support for context blocks
        """
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        At end of context block, reset the lxml document
        """
        self.reset()


class PassStateWSGIApp(object):
    """
    WSGI application that replays the TestAgent's cookies and currently
    loaded response to the downstream UA on the first request,
    thereafter proxies requests to the agent's associated wsgi
    application.

    Used by ``TestAgent.serve``.
    """

    def __init__(self, testagent):
        self.first_request_served = False
        self.testagent = testagent

    def __call__(self, environ, start_response):
        if self.first_request_served:
            return self.testagent.validated_app(environ, start_response)
        self.first_request_served = True
        return self.first_request(environ, start_response)

    def first_request(self, environ, start_response):
        response = self.testagent.response
        mimetype, charset = parse_header(response.get_header('Content-Type'))
        charset = dict(charset).get('charset', 'UTF-8')
        if is_html(response) and self.testagent._lxml is not None:
            response = response.replace(content=[tostring(self.testagent.lxml,
                                                          encoding=charset)])

        for key, morsel in self.testagent.cookies.items():
            response = response.add_header('Set-Cookie', morsel.OutputString())
        return response(environ, start_response)


def url_join_same_server(baseurl, url):
    """
    Join two urls which are on the same server. The resulting URI will have the
    protocol and netloc portions removed. If the resulting URI has a different
    protocol/netloc then a ``ValueError`` will be raised.

        >>> from flea import url_join_same_server
        >>> url_join_same_server('http://localhost/foo', 'bar')
        '/bar'
        >>> url_join_same_server('http://localhost/foo',
        ...                      'http://localhost/bar')
        '/bar'
        >>> url_join_same_server('http://localhost/rhubarb/custard/',
        ...                      '../')
        '/rhubarb/'
        >>> url_join_same_server('http://localhost/foo',
        ...                      'http://example.org/bar')
        Traceback (most recent call last):
          ...
        ValueError: URI links to another server: http://example.org/bar

    """
    url = url_join(baseurl, url)
    url = urlparse(url)
    if urlparse(baseurl)[:2] != url[:2]:
        raise ValueError("URI links to another server: %s" %\
                         (urlunparse(url),))
    return urlunparse(('', '') + url[2:])


def parse_cookies(response):
    """
    Return a ``Cookie.BaseCookie`` object populated from cookies parsed from
    the response object
    """
    base_cookie = BaseCookie()
    for item in response.get_headers('Set-Cookie'):
        base_cookie.load(item)
    return base_cookie


def is_html(response):
    """
    Return True if the response content-type header indicates an (X)HTML
    content part.
    """
    return re.match(
        r'^(text/html|application/xhtml\+xml)\b',
        response.get_header('Content-Type')
    ) is not None


def escapeattrib(s):
    return s.replace('&', '&amp;').replace('"', '&quot;')


def guess_expression_flavor(expr):
    """
    Try to guess whether ``expr`` is a CSS selector or XPath expression.

    ``css`` is the default value returned for expressions valid in both
    syntaxes.
    """
    try:
        XPath(expr)
    except XPathError:
        return 'css'

    try:
        CSSSelector(expr)
    except (AssertionError, SelectorSyntaxError):
        return 'xpath'

    if '/' in expr:
        return 'xpath'
    if '@' in expr:
        return 'xpath'
    return 'css'
