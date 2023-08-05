Flea documentation contents
###########################

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. toctree::
        :maxdepth: 3

.. include:: ../README.txt


Overview
===========

The ``TestAgent`` class provides a user agent that drives a WSGI
application::

    >>> from flea import TestAgent
    >>> agent = TestAgent(my_wsgi_app)

You can now use this agent to navigate your WSGI application by...


.. testsetup:: *

    from fresco import FrescoApp, Request, Response
    from flea import TestAgent

    def redirect_app(environ, start_response):
        return Response.redirect('/')(environ, start_response)

    form_html = """
            <html><body>
                <a id="mylink" href="/">foo</a>
                <a class="highlighted" href="/">link text</a>
                <form name="login-form" action="/"><input type='text' name='username'/><input type='text' name='password'/></form>
                <form name="contact" action="/"><button type="submit" name="send">send</button></form>
                <form name="register" action="/register"></form>
                <form name="upload" action="/">
                    <input type="file" name="image"/>
                    <input type="text" name="title"/>
                    <input type="radio" name="size" value="small"/>
                    <input type="radio" name="size" value="medium"/>
                    <input type="radio" name="size" value="large"/>
                    <input type="checkbox" name="spam_me" value="lots"/>
                    <input type="checkbox" name="terms_and_conditions" value="yes"/>
                    <select name="days" multiple="">
                        <option value="monday">monday</option>
                        <option value="tuesday">tuesday</option>
                        <option value="wednesday">wednesday</option>
                        <option value="thursday">thursday</option>
                        <option value="friday">friday</option>
                    </select>
                    <select name="color">
                        <option value="red">red</option>
                        <option value="green">green</option>
                    </select>
                </form>
            </body></html>"""

    testapp = FrescoApp()
    testapp.route_wsgi('/register', redirect_app)
    testapp.route_wsgi('/', Response([form_html]))
    r = TestAgent(testapp).get('/')

...making GET requests:

.. doctest::

    >>> r = r.get('/my-page')

...making POST requests:

.. doctest::

    >>> r = r.post('/contact', data={'message': 'your father smells of elderberries'})

...clicking links:

.. doctest::

    >>> # Click on a link with content 'foo'
    >>> r = r.click("foo")

    >>> # Click a link matching a regular expression
    >>> import re
    >>> r = r.click(re.compile('f.*o'))

    >>> # Find a link using a CSS selector
    >>> r = r("a#mylink").click()

    >>> # Or an XPath expression
    >>> r = r("//a[@id='mylink']").click()


...and submitting forms:

.. doctest::

    >>> r = r("form[name=login-form]").fill(username='me', password='123').submit()
    >>> r = r("form[name=contact] button[name=send]").submit()

Finding elements
----------------

There are several methods for traversing the DOM. The simplest is usually to use CSS selectors:

.. doctest::

    >>> r.css("a.highlighted")
    <ResultWrapper ...>

For more complex requirements you can also use XPath, with :meth:`find` or with dictionary-style access:

.. doctest::

    >>> r.find("//a[@class='highlighted']")
    <ResultWrapper ...>
    >>> r["//a[@class='highlighted']"]
    <ResultWrapper ...>


You can also call the :class:`TestAgent` directly, passing either an XPath
expression or a CSS selector. Flea will autosense the expression type:

.. doctest::

    >>> r("a.highlighted")
    <ResultWrapper ...>
    >>> r("//a[@class='highlighted']")
    <ResultWrapper ...>

If an expression could be interpreted as both a valid XPath and CSS selector,
flea defaults to 'css'. You can force an expression to be interpreted as one or
the other by passing a ``flavor`` argument:

.. doctest::

    >>> r("a.highlighted", 'css')
    <ResultWrapper ...>
    >>> r("//a[@class='highlighted']", 'xpath')
    <ResultWrapper ...>


Filling and submitting forms
=============================

Although you can fill fields by altering the necessary DOM properties: ``checked``
(checkboxes, radio buttons), ``selected`` (select options), ``text`` (textareas)
and ``value`` for other input types, it's usually more convenient to use the 
:meth:`fill` method, which presents a common interface to all control types.

When you fill in form fields, the underlying DOM is updated. This makes it
really easy to check your form is correctly filled while developing tests:

.. doctest::

    >>> app = Response([
    ...     '<html>'
    ...     '<form>'
    ...         '<input type="text" name="subject" />'
    ...         '<textarea name="message"/>'
    ...     '</form>'
    ...     '</html>'
    ... ])
    >>> r = TestAgent(app).get('/')
    >>> r('form').fill(subject='hello', message='how are you?')
    <...>

    >>> # Display the updated HTML
    >>> # You could also use r.serve() to interact with the completed form in a web browser
    >>> r('form').html()
    u'<form><input type="text" name="subject" value="hello"><textarea name="message">how are you?</textarea></form>'



Text inputs and textareas:

.. doctest::

    >>> app = Response([
    ...     '<html>'
    ...     '<form>'
    ...         '<input type="text" name="subject" />'
    ...         '<textarea name="message"/>'
    ...     '</form>'
    ...     '</html>'
    ... ])
    >>> r = TestAgent(app).get('/')
    >>> r('input[name=subject]').fill('hello')
    <...>
    >>> r('textarea[name=message]').fill('world')
    <...>
    >>> r('form').submit_data()
    [('subject', 'hello'), ('message', 'world')]

Checkboxes:

.. doctest::

    >>> app = Response([
    ...     '<html>'
    ...     '<form>'
    ...         '<input type="checkbox" name="opt-in" value="yes" />'
    ...         '<input type="checkbox" name="items" value="one" />'
    ...         '<input type="checkbox" name="items" value="two" />'
    ...         '<input type="checkbox" name="items" value="three" />'
    ...     '</form>'
    ...     '</html>'
    ... ])
    >>> r = TestAgent(app).get('/')
    >>> r('input[name=opt-in]').fill(True)
    <...>
    >>> r('input[name=items]').fill(['two', 'three'])
    <...>
    >>> r('form').submit_data()
    [('opt-in', 'yes'), ('items', 'two'), ('items', 'three')]

Radio buttons:

.. doctest::

    >>> app = Response([
    ...     '<html>'
    ...     '<form>'
    ...         '<input type="radio" name="item" value="one" />'
    ...         '<input type="radio" name="item" value="two" />'
    ...         '<input type="radio" name="item" value="three" />'
    ...     '</form>'
    ...     '</html>'
    ... ])
    >>> r = TestAgent(app).get('/')
    >>> r('input[name=item]').fill('two')
    <...>
    >>> r('form').submit_data()
    [('item', 'two')]

Select boxes

.. doctest::

    >>> app = Response([
    ...     '<html>'
    ...     '<form>'
    ...         '<select name="icecream">'
    ...             '<option value="strawberry">strawberry</option>'
    ...             '<option value="vanilla">vanilla</option>'
    ...         '</select>'
    ...         '<select name="cake" multiple="">'
    ...             '<option value="chocolate">chocolate</option>'
    ...             '<option value="ginger">ginger</option>'
    ...             '<option value="coffee">coffee</option>'
    ...         '</select>'
    ...     '</form>'
    ...     '</html>'
    ... ])
    >>> r = TestAgent(app).get('/')
    >>> r('select[name="icecream"]').fill('strawberry')
    <...>
    >>> r('select[name="cake"]').fill(['chocolate', 'coffee'])
    <...>
    >>> r('form').submit_data()
    [('icecream', 'strawberry'), ('cake', 'chocolate'), ('cake', 'coffee')]


File uploads
-------------

To test file upload fields, you must pass a tuple of ``(filename,
content-type, data)`` to :meth:`fill`. The data part can either be a
string:

.. doctest::

    >>> r = TestAgent(Response([
    ...         '<html>'
    ...         '<form name="upload" action="/" enctype="multipart/form-data">'
    ...                 '<input type="file" name="image"/>'
    ...         '</form>'
    ...         '</html>'
    ... ])).get('/')
    >>> r("input[name=image]").fill(('icon.png', 'image/jpeg', 'testdata'))
    <...>


Or a file-like object:

.. doctest::

    from StringIO import StringIO
    r("input[name=image]").fill(('icon.png', 'image/jpeg', StringIO('aaabbbccc')))


Filling forms in a single call
------------------------------

The :meth:`.fill` method, when called on a form element, is a useful shortcut to
filling in an entire form with a single call. Keyword arguments are used to
populate input controls by id or name:


.. testcode::

    r = TestAgent(Response([
        '<html>'
                '<form name="login-form">'
                        '<input type="text" name="username"/>'
                        '<input type="text" name="password"/>'
                '</form>'
        '</html>'
    ])).get('/')
    r = r["//form[@name='login-form']"].fill(
        username='fred',
        password='secret'
    ).submit()

XPath or CSS selector expressions may be used for fields whose names can't be
represented as python identifiers or when you need more control over exactly
which fields are selected:

.. testcode::

    r = r("form[name=login-form]").fill(('.//input[1]', 'fred'),
                                        ('.//input[2]', 'secret')).submit()


HTTP redirects
--------------

HTTP redirect responses (301 or 302) are followed by default. If you want to
explicitly check for a redirect, you'll need to specify ``follow=False`` when
making the request. All methods associated with making a request - ``click``,
``submit``, ``get``, ``post`` etc - take this parameter.

To follow a redirect manually:
 
.. doctest::

    >>> r = TestAgent(testapp).get('/')
    >>> r = r("form[name=register]").submit(follow=False)
    >>> r.request.path
    u'/register'
    >>> r.response.status_code
    302
    >>> r = r.follow()
    >>> r.request.path
    u'/'
    >>> r.response.status_code
    200
 

Querying WSGI application responses
-----------------------------------

Checking the content of the request
`````````````````````````````````````

::

    >>> assert r.request.path_info == '/index.html'
    >>> print r.request.environ
    {...}

``r.request`` is a `pesto.request.Request <http://pypi.python.org/pypi/pesto>`_
object, and all attributes of that class are available to examine.

Checking the content of the response
`````````````````````````````````````

::

    >>> assert r.response.content_type == 'text/html'
    >>> assert r.response.status == '200 OK'

Note that ``r.response`` is a `pesto.testing.TestResponse
<http://pypi.python.org/pypi/pesto>`_ object, and all attributes of that class
are available.


By default, responses are checked for a successful status code (2xx or 3xx),
and an exception is raised for any other status code. If you want to bypass
this checking, use the ``check_status`` argument:

.. doctest::

    >>> def myapp(environ, start_response):
    ...     start_response('500 Error', [('Content-Type', 'text/plain')])
    ...     return ['Sorry, an error occurred']
    ...
    >>> TestAgent(myapp).get('/')
    Traceback (most recent call last):
    ...
    BadStatusError: GET '/' returned HTTP status '500 Error'
    >>> TestAgent(myapp).get('/', check_status=False)
    <flea.TestAgent ...>


Checking returned content.
``````````````````````````````

The ``.body`` property contains the raw response
from the server::
    
.. doctest::

    >>> r = TestAgent(Response(["<html><p><strong>How now</strong> brown cow</p></html>"])).get('/')
    >>> assert 'cow' in r.body

Any element selected via an xpath query has various helper methods useful for
inspecting the document.

Checking if strings are present in an HTML element
``````````````````````````````````````````````````

.. doctest::

    >>> assert 'cow' in r('p')

Accessing the html of selected elements
```````````````````````````````````````

.. doctest::

    >>> r('//p[1]').html()
    u'<p><strong>How now</strong> brown cow</p>'

Note that this is the html parsed and reconstructed by lxml, so is unlikely to
be the literal HTML emitted by your application - use :attr:`body` for that.

Accessing textual content of selected elements
````````````````````````````````````````````````
The :meth:`striptags` method removes all HTML tags and normalizes whitespace to make string comparisons easier:

.. doctest::

    >>> r = TestAgent(Response([
    ... """
    ...     <html>
    ...         <p>
    ...             <strong>How now</strong>
    ...             brown
    ...             cow
    ...          </p>
    ...    </html>
    ... """])).get('/')
    >>> r('//p[1]').striptags()
    ' How now brown cow '


WSGI environ
------------

Flea sets the key ``flea.testing`` in the WSGI environment so that WSGI
applications can sense if they are in a test environment.

This app will say "testing, testing" when called by flea, otherwise it says
"hello!":

.. doctest::

    >>> def app(environ, start_response):
    ...     start_response('200 OK', [('Content-Type', 'text/plain')])
    ...     if environ.get('flea.testing'):
    ...          return ['testing, testing']
    ...     return ['hello!']
    ...
    >>> TestAgent(app).get('/').body
    u'testing, testing'


Inspecting and interacting with a web browser
---------------------------------------------

Flea gives you two methods for viewing the application under test in a web
browser.

The ``showbrowser`` method opens a web browser and displays the content of the
most recently loaded request::

    >>> r.get('/').showbrowser()

The ``serve`` method starts a HTTP server running your WSGI application and
opens a web browser at the location corresponding to the most recent request.
For example, the following code causes a web browser to open at
``http://localhost:8080/foobar``::

    >>> r.get('/foobar').serve()

If you want to change the default hostname and port for the webserver you must
specify these when first initializing the ``TestAgent`` object::

    >>> r = TestAgent(my_wsgi_app, host='192.168.1.1', port='8888')
    >>> r.get('/foobar').serve()

Now the web browser would be opened at ``http://192.168.1.1:8888/foobar``.

One final note: the first request to the application is handled by relaying the
most recent response received to the web browser, including any cookies
previously set by the application. Also, if any methods have been called
that access the lxml representation of an HTML response – eg finding elements
by an XPath query or filling form fields – then the lxml document in its
current state will be converted to a string and served to the browser, meaning
that while the document should be logically equivalent, it will no longer be a
byte-for-byte copy of the response content received from the WSGI application.

This **only** applies to the first request, and ensures that the web browser
receives a copy of the page as currently in memory, with any form fields
filled in and with any cookies set so that you can pick up in your web
browser exactly where the ``TestAgent`` object left off.



API documention
----------------

.. automodule:: flea
        :members:
