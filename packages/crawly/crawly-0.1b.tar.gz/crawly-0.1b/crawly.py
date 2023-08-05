# -*- encoding: utf8 -*-
"Crawly is a small library to crawl websites."
import sys
import json
import inspect
import urlparse
import logging.config
import itertools as it
from functools import partial
from datetime import datetime
from collections import Counter

import lxml
import lxml.html

import gevent
from gevent import monkey
from gevent.pool import Pool, Group
from gevent.queue import Queue, Empty
from gevent.event import AsyncResult

# Patch std library before importing requests.
monkey.patch_all(thread=False, select=False)

from requests import Session


__author__ = 'Mouad Benchchaoui'
__version__ = '0.1b'
__copyright__ = u'Copyright © 2012, Mouad Benchchaoui'
__license__ = 'BSD license'


__all__ = ['Pagination', 'WebPage', 'WebSite', 'XPath', 'HTML', 'runner']


# Global Configuration.
_CONFIG = {
    'delay': 0,     # time to wait in second between two consecutive requests.
    'timeout': 15,  # time to wait in second before raising TimeOut error.
    # Requests configuration: http://tinyurl.com/dyvdj57
    'requests': {
        'base_headers': {
            'Accept': '*/*',
            'Accept-Encoding': 'identity, deflate, compress, gzip',
            'User-Agent': 'crawly/' + __version__
        },
        'danger_mode': False,
        'encode_uri': True,
        'keep_alive': True,
        'max_redirects': 30,
        'max_retries': 3,
        'pool_connections': 10,
        'pool_maxsize': 10,
        'safe_mode': True,   # Default was False.
        'strict_mode': False,
        'trust_env': True,
        'verbose': False
    },
    # Logging configuration: http://tinyurl.com/crt6rkw
    'logging': {
        'version': 1,
        'formatters': {
            'standard': {
                'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
            }
        },
        'handlers': {
            'console': {
                'formatter': 'standard',
                'class': 'logging.StreamHandler',
            }
        },
        'loggers': {
            '': {
                'handlers': ['console'],
                'level': 'DEBUG',
                'propagate': False,
            }
        }
    }
}


class ExtractionError(Exception):
    "Error raised when extracting data from HTML fail."


class _AsyncRequest(AsyncResult):
    """Asynchrone request.

    This class is a wrapper around :class:`requests.Request` and in the same
    time a subclass of :class:`gevent.event.AsyncResult`.
    When this class instance is first created no request is sent until the
    attribute :attr:`_AsyncRequest.response` is accessed, than the class use
    the :obj:`runner` pool to send a request in a greenlet to fetch the url
    content and the method :attr:`gevent.gevent.AsyncResult.get` is called,
    which will block and trigger a context-switch, and register the current
    greenlet to wake up when the request is finished.

    Arguments:
        *args, **kws: Same arguments as :func:`requests.Session.request`.

    Example:

        >>> request = _AsyncRequest('GET', 'http://google.com')
        >>> request.response
        <Response [200]>

    """

    def __init__(self, *args, **kws):
        super(_AsyncRequest, self).__init__()
        # Set the response as a result when the response is received, to wake
        # up waiting greenlets.
        kws.setdefault('hooks', {}).update({'response': self.set})
        self._request = runner._build_request(*args, **kws)

    def _send(self):
        "Send this request in a greenlet (using the :data:`runner` pool)."
        return runner.fetch(self)

    @property
    def pretty_url(self):
        "Get a beautiful URL representation in the form <(method: data) url>."
        method = self._request.method
        if self._request.data:
            method = '(%s: %s)' % (method, self._request.data)
        return '<%s %s>' % (method, self._request.full_url)

    def __getattr__(self, attr):
        "Return :class:`requests.Session.Request` instance attribute."
        return getattr(self._request, attr)

    @property
    def response(self):
        """Get the response and send request if it's not already sent.

        If the request wasn't sent yet, accessing this attribute will first
        trigger sending the request and than it will wait and block until the
        response is available. Blocking mean that if this attribute is accessed
        in a greenlet it will trigger a context switch and the current greenlet
        will be awaken when the response is received.

        """
        if not self.sent:
            self._send()
        return self.get()


class Pagination(object):
    """Class that iterate over a website pages and return a request for
    each one of them.

    Arguments:
        - url: Pagination url.
        - data: Dictionary of data to send with the URL to get the next page,
          you can pass the string template ``{page}`` as a value of any of this
          dictionary key, which will be replaced by the exact page value before
          sending the request.
        - method: HTTP method to use to request the url, default: GET.
        - start: Page number to start requesting from included, default: 1.
        - end: Last pagination's page number **included**, default to
          ``None`` in this case developers must override the ``end_reached``
          method to be able to stop somewhere.

    Example ::

        >>> stackoverflow_pages = Pagination(
        ...     'http://stackoverflow.com/questions/tagged/python',
        ...     data={'page': '{page}'},
        ...     end=4
        ... )
        >>> [r.pretty_url for r in stackoverflow_pages]  # doctest: +NORMALIZE_WHITESPACE
        ['<GET http://stackoverflow.com/questions/tagged/python?page=1>',
         '<GET http://stackoverflow.com/questions/tagged/python?page=2>',
         '<GET http://stackoverflow.com/questions/tagged/python?page=3>',
         '<GET http://stackoverflow.com/questions/tagged/python?page=4>']

    """

    def __init__(self, url, data, method='GET', start=1, end=None):
        self._url = url
        self._data = data
        self._method = method
        self._current_page = start
        self._end = end
        self._current_request = None

    def __iter__(self):
        return self

    def _build_request(self):
        "Get the request for the next page."
        data = {}
        # Replace {page} placeholder with current page value.
        for k, v in self._data.iteritems():
            data[k] = v.format(page=self._current_page)
        # Apply parameters or data at the URL in the two cases (GET or POST).
        isGET = self._method.lower() == "get"
        return _AsyncRequest(
            method=self._method,
            url=self._url,
            **({'params': data} if isGET else {'data': data})
        )

    def end_reached(self):
        """Method meant to be overrided to stop iterating over pagination
        if ``end`` constructor argument wasn't set.

        Return True to stop paginating else False.

        """
        raise NotImplementedError("Pagination class need the method"
            " `end_reached` to be implemented because the pagination ``end``"
            " argument wasn't given."
        )

    def _stop(self):
        """Check when iterating pagination should stop.

        The default behavior of this method is to check if the last page was
        reached if ``self._end`` was given else it dispatch the decision to
        ``end_reached`` method.

        Return:
           True to stop pagination else it will continue to the next page.

        """
        if self._end is None:
            return self.end_reached()
        return self._current_page > self._end

    def next(self):
        "Get the next page request."
        self._current_request = self._build_request()
        if self._stop():
            raise StopIteration
        self._current_page += 1
        return self._current_request


class XPath(object):
    r"""Callable class that define XPATH query with callbacks.

    Arguments:
        - xpath: A string representing the XPath query.
        - callbacks: A list of functions to call in order (first to last)
          over the result returned by :class:`lxml.etree.XPath`, this class
          have also a :attr:`callbacks` class variable that can be set by
          subclasses which have priority over the callbacks passed in this
          argument, which mean that callbacks passed here will be called after
          the class variable callbacks.

          Illustration ::

              XPath("...", callback1, callback2, callback3)
                  <=>
              callback3( callback2( callback1( XPath("...") ) ) )
    Raise:
          :exc:`ExtractionError` if extraction failed.

    Example ::

        >>> x = XPath('//div/h2/text()', str.strip)
        >>> x('<html><body><div><h2>\r\ntest\n</h2></div></body></html>')
        'test'

        >>> x = XPath('//ul/li/text()', lambda ls: map(int, ls))
        >>> x('<html><body><ul><li>1</li><li>2</li></ul></body></html>')
        [1, 2]

        >>> x = XPath('//not-found')
        >>> x('<html></html>')

    """

    callbacks = []

    def __init__(self, xpath, *callbacks):
        self._xpath = lxml.etree.XPath(xpath)
        self._callbacks = self.callbacks + list(callbacks)

    def __call__(self, html, *args, **kws):
        if isinstance(html, basestring):
            html = lxml.html.fromstring(html)
        result = self._xpath(html, *args, **kws)
        # Simplify result when matched data is a list of 1 or 0 element.
        if isinstance(result, list):
            if len(result) == 1:
                result = result[0]
            elif len(result) == 0:
                result = None
        try:
            for i, func in enumerate(self._callbacks):
                result = func(result)
        except Exception as ex:
            # Catch all exception and raise a more meaningful exception.
            raise ExtractionError('Callback #%d failed: %s' % (i, ex))
        return result


class HTML(object):
    """Class to represent HTML code.

    This class is a wrapper around :class:`lxml.html.HtmlElement` class, so
    developers can interact with instance of this class in the same way as
    :class:`lxml.html.HtmlElement` instances, with the addition that this class
    define a new method :meth:`HTML.extract` to extract data from the html.

    Example ::

        >>> html = HTML('<html><body><div><h2>test</h2></div></body></html>')
        >>> html.extract('//div/h2/text()')
        'test'

    """

    def __init__(self, html):
        self._html = lxml.html.fromstring(html)

    def __getattr__(self, attr):
        "Get :class:`lxml.html.HtmlElement` instance attribute."
        return getattr(self._html, attr)

    def extract(self, extractor):
        """Extract data referred by ``extractor``.

        Argument:
            extractor: Can be a dictionary in the form
            ``{'name': <callable> or <string>}``, or unique callable object
            that accept a :class:`lxml.html.HtmlElement` e.g. :class:`XPath`
            instances or a string which will be automatically transformed to
            an :class:`XPath` instance.
        Return:
            The extracted data in the form of a dictionary if the ``extractor``
            argument given was a dictionary else it return a list or string
            depending on the extractor callbacks.
        Raise:
            :exc:`ExtractionError` if extraction failed.

        """
        if not isinstance(extractor, dict):
            # String is transformed to XPath.
            if isinstance(extractor, basestring):
                extractor = XPath(extractor)
            return extractor(self._html)
        result = {}
        try:
            for key, ext in extractor.iteritems():
                if isinstance(ext, basestring):
                    ext = XPath(ext)
                result[key] = ext(self._html)
        except Exception as ex:
            # Catch all exception and raise a more meaningful exception.
            raise ExtractionError('Extracting "%s" failed: %s' % (key, ex))
        return result


# TODO: How to use another request ? create an interface of request maybe ?
# How about runner ? why someone will want to do that ?
# TODO: Start refactoring from here.
class WebPage(object):
    """Class that represent a WEB site page that can be used to extract data
    or extract links to follow.

        Extract data from the page ::

            >>> class PythonJobs(WebPage):
            ...     toextract = {
            ...         'title': '//div[5]/div/div/div[2]/h2/a/text()'
            ...     }
            ...
            >>> page = PythonJobs('http://www.python.org/community/jobs/')
            >>> page.extract()  # doctest: +ELLIPSIS
            {'title': ...}

        Extract links to follow ::

            >>> class PythonJobs(WebPage):
            ...     tofollow = '//div[5]/div/div/div[2]/h2/a/@href'
            ...
            >>> page = PythonJobs('http://www.python.org/community/jobs/')
            >>> list(page.follow_links())  # doctest: +SKIP
            [...]

    Arguments:
        - url_or_request: This argument can be a string representing the URL
          of a web page or for better customizing it can be also a request.
        - parent: A :class:`WebPage` or a :class:`WebSite` instance that
          represent the parent site/page of this one.
        - initial: Initial data related to this page.

    """

    # Define extractor callbacks of data to extract from this WEB page.
    toextract = None
    # Define XPath (or an extractor callback) of links to follow.
    tofollow = None
    # Class that will wrap new WEB pages generated by following links.
    WebPageCls = None

    def __init__(self, url_or_request, parent=None, initial=None):
        if isinstance(url_or_request, basestring):
            self._request = self._build_request(url_or_request)
        else:
            self._request = url_or_request
        self._html = None
        self._data = initial or {}
        self._parent = parent
        # Set to false when self.data is first accessed.
        self.__firstime = True

    def __str__(self):
        return '%s: %s' % (self.__class__, self.url)

    __repr__ = __str__

    @property
    def url(self):
        "Get a pretty URL of this page in the form <(method: data) url>."
        return self._request.pretty_url

    @property
    def request(self):
        "Get the request used by this page."
        return self._request

    @property
    def html(self):
        "Get the HTML of this page as a :class:`HTML` class instance."
        if self._html is None:  # Compute only once.
            response = self._request.response
            self._html = HTML(response.text)
        return self._html

    def extract(self, toextract=None, update=True):
        """Extract the data given by ``toextract``.

        Argument:
            - toextract: same argument accepted by :meth:`HTML.extract` method.
            - update: Boolean that enable updating the internal data holder
              when it's set to True (default) else it will return extracted
              data w/o updating internal data holder.
        Return:
            Extracted data.
        Raise:
            - :exc:`ExtractionError` if extraction failed.
            - ``ValueError`` if the argument didn't follow the documentation
              guidline.

        """
        toextract = toextract or self.toextract
        if toextract is None:
            raise ValueError('No sections was given')
        data = self.html.extract(toextract)
        if update:
            self._data.update(data)
        return data

    def follow_links(self, tofollow=None):
        """Follow the links given and return a :class:`WebPage.WebPageCls`
        instance for each link.

        Argument:
            tofollow: same argument accepted by :meth:`HTML.extract` method,
            if :attr:`tofollow` is a dictionary it must contain a key "links"
            which should point to the path to use to extract URLs to follow
            and any extra keys in the dictionary will be used to extract extra
            data that **must be of the same length as the URLs to follow** and
            this data will be passed to the generated :attr:`WebPageCls`
            instances.
        Return:
            Generate a list of :attr:`WebPageCls` instances for each
            link to follow.
        Raise:
            - :exc:`ExtractionError` if extraction failed.
            - ``ValueError`` if the argument didn't follow the documentation
              guideline.

        """
        tofollow = tofollow or self.tofollow
        if isinstance(tofollow, dict) and 'links' in tofollow:
            extra = tofollow.copy()
            links = extra.pop('links')
        elif callable(tofollow) or isinstance(tofollow, basestring):
            links = tofollow
            extra = {}
        else:
            raise ValueError('No links to follow')
        # Extract links to follow.
        links = self.extract(links, update=False) or []
        if isinstance(links, basestring):  # Case only one link was found.
            links = [links]
        # Extracted data to pass to child web pages.
        if extra:
            extra = self.extract(extra, update=False)
            # {'i':[1,2],'s':['a','b']} => [{'i':1,'s':'a'},{'i':2,'s':'b'}]
            extra = [dict(zip(extra, vals)) for vals in zip(*extra.values())]
        else:
            # In case tofollow  was a dictionary with 'links' and the only key.
            extra = [{} for _ in links]
        # Links and extracted data should have same length.
        if len(extra) != len(links):
            raise ValueError("Number of links to follow is different"
                " than the length of extracted data: %r != %r" % (
                links, extra)
            )
        # Extract links to follow and data to pass to child web pages.
        WebPageCls = self.WebPageCls or self.__class__
        for link, data in zip(links, extra):
            yield WebPageCls(
                urlparse.urljoin(self._request.url, link),
                parent=self,
                initial=data
            )

    def _build_request(self, url, method='GET'):
        "Build a request to ``url`` using HTTP ``method``."
        return _AsyncRequest(method, url)

    def _getdata(self):
        """Method that is meant to be overrided by third-party that should
        return extra data as a dictionary to update the extracted data with.

        This method is called only once when accessing the :meth:`WebPage.data`
        attribute the first time.

        """
        return NotImplemented

    @property
    def data(self):
        """Get extracted data.

        **WARNING**: This property will recalculate each time the data to
        return when it's accessed, so be careful about side effect, what i
        mean by that is if you override this method and for example the new
        method define a new value that change in each call e.g.
        ``datetime.now()``, than you will have inconsistency in your data.
        In this case and if inconsistency is a problem, developers should use
        :meth:`WebPage._getdata` method instead to define any extra data, which
        is computed only the first time this property is accessed.

        """
        if self.__firstime:
            extra = self._getdata()
            if extra is not NotImplemented:
                self._data.update(extra)
        self.__firstime = False
        return self._data


class WebSite(object):
    """An abstract super class that represent a website.

    Class inheriting from this class should implement the ``url`` class
    variable, else this class will raise an Exception.

    Examples ::

        >>> class PythonQuestions(WebSite):
        ...     url = "http://stackoverflow.com/question/tagged/python"
        ...     Pagination = Pagination(
        ...         'http://stackoverflow.com/questions/tagged/python',
        ...         data={'page': '{page}'},
        ...         end=4
        ...     )
        ...
        >>> [page.url for page in PythonQuestions().pages]      # doctest: +NORMALIZE_WHITESPACE
        ['<GET http://stackoverflow.com/questions/tagged/python?page=1>',
         '<GET http://stackoverflow.com/questions/tagged/python?page=2>',
         '<GET http://stackoverflow.com/questions/tagged/python?page=3>',
         '<GET http://stackoverflow.com/questions/tagged/python?page=4>']

    """

    WebPageCls = WebPage  # Class to return for each extracted page.
    Pagination = None     # Set to a Pagination class instance.
    url = None            # Website URL.

    def __new__(cls):
        if cls.url is None:
            raise Exception(
                "'url' wasn't set for website class."
            )
        return super(WebSite, cls).__new__(cls)

    @property
    def pages(self):
        """Get pages from the website.

        If :attr:`WebSite.Pagination` class variable was set, this return a
        list of pages yield by the pagination, else it return a list with
        a single element which is a :class:`WebPage` instance of this url.

        """
        WebPageCls = partial(self.WebPageCls, parent=self)
        if self.Pagination is not None:
            return it.imap(WebPageCls, self.Pagination)
        return [WebPageCls(self.url)]


class _Runner(object):
    """Class to manage running all requests concurrently and extracting data
    from the website and writing them back to pipelines.

    """

    def __init__(self):
        self.__config = _CONFIG.copy()
        # Configure logging.
        logging.config.dictConfig(self.__config['logging'])
        # Hold greenlets that fetch pages which limit concurrent requests.
        self._requests = Pool(self.__config['requests']['pool_maxsize'])
        # Request session.
        self._session = Session(config=self.__config['requests'])
        # Hold greenlets that extract data.
        self._extractors = Group()
        # Hold greenlets that write to pipelines.
        self._pipes = Group()
        # Hold web page to process.
        self._toprocess = Queue(-1)
        # Hold pipeline functions to call after extraction.
        self._pipelines = []
        # Predicate that check when stop crawling.
        self._takewhile = lambda *args: True
        # Predicate to define URLs to crawl.
        self._filter = lambda *args: False
        # Report data.
        self._report = {
            'CRAWLED URLS': 0,
            'EXTRACTED DATA': 0,
            'EXCEPTIONS COUNTER': Counter(),
            'START TIME': None,
            'FINISH TIME': None,
            'SHUTDOWN REASON': 'FINISH CRAWLING'
        }
        # Function to call when a greenlet raise an exception.
        self._exception_func = None
        # Function to call when the crawling finished.
        self._finish_func = None

    def _configure(self, argv, **kwargs):
        """Read and apply configuration passed to command line.

        This method is automatically called when :meth:`runner.start`` is
        called.

        Argument:
            argv: Command line arguments, check :meth:`start` for the accepted
            arguments.
            kwargs: Extra argument for configuration, check :meth:`start`.
        Raise:
            ``ValueError`` if wrong usage.

        """
        if not argv and not kwargs:  # No user defined argument was given
            return
        if argv:
            if len(argv) != 1:
                raise ValueError('Too many argument')
            opt, filename = argv[0].split('=')
            if opt != '--config':
                raise ValueError('Unknown option: %s' % opt)
            with open(filename) as fp:
                self.__config.update(json.load(fp))
        # Update with extra configuration.
        self.__config.update(kwargs)
        # Re-configure.
        logging.config.dictConfig(self.__config['logging'])
        self._requests = Pool(self.__config['requests']['pool_maxsize'])
        self._session = Session(config=self.__config['requests'])

    def set_website(self, website):
        """Set the website to crawl, the ``website`` argument can be an
        instance or a class that inherit from :class:`WebSite` class.

        Return:
           ``self`` to allow Fluent Interface creation pattern.

        """
        if inspect.isclass(website):
            website = website()
        self._website = website
        return self

    def add_pipeline(self, pipeline):
        """Add a pipeline which is a callable that accept a :class:`WebPage`
        class or subclass instance, which will be passed after extracting all
        the data instructed.

        Return:
           ``self`` to allow "Fluent Interface" creation pattern.

        """
        self._pipelines.append(pipeline)
        return self

    def takewhile(self, predicate):
        """Add a predicate that will stop adding URLs to fetch when the
        predicate will return False.

        Argument:
           predicate: A function that accept a page as an argument and return
           a boolean; when the predicate return False all URLs after this one
           in the website will not be fetched.
        Return:
           ``self`` to allow "Fluent Interface" creation pattern.

        WARNING: The page when passed to the ``predicate`` is not fetched yet,
        so no data is extracted from this page yet.

        """
        self._takewhile = predicate
        return self

    def filter(self, predicate):
        """Add a predicate to filter pages (URLs) to include only the ones
        with which the predicate return True.

        The difference between this method and :meth:`_Runner.takewhile` is that
        :meth:`_Runner.filter` method allow only to filter individual URLs while
        :meth:`_Runner.takewhile` will stop at a given URL when the predicate
        return False and all URLs which come after this last URL will not be
        crawled.

        Return:
           ``self`` to allow "Fluent Interface" creation pattern.

        """
        self._filter = predicate
        return self

    def on_finish(self, func):
        """Add a function to be executed when the crawler finish crawling and
        all the greenlet has been joined.

        Argument:
            func: A function that should accept no arguments.
        Return:
            ``self`` to allow "Fluent Interface" creation pattern.

        """
        self._finish_func = func
        return self

    def on_exception(self, func):
        """Add a function to be executed when the crawler find an exception.

        Argument:
            func: A function that should accept one arguments, that will be
            the greenlet that raised the exception.
        Return:
            ``self`` to allow "Fluent Interface" creation pattern.

        """
        self._exception_func = func

    def _build_request(self, method, url, **kws):
        """Build a request from the configured :class:`requests.Session`.

        Arguments: The same as :func:`requests.Session.request` method.
        Return: An **unsent** request unless ``return_response`` was explicitly
        set to True.

        """
        kws['timeout'] = self.__config['timeout']   # Request timeout.
        kws.setdefault('return_response', False)  # Don't send request.
        return self._session.request(method, url, **kws)

    def fetch(self, request):
        "Execute send ``request`` in a greenlet from the pool of requests."
        # Create an inner function to only show the logging message when the
        # pool start fetching the request, b/c the pool have a limited size.
        def _send(*args, **kws):
            self.log('Fetching %s' % request.pretty_url)
            request.send(*args, **kws)
        g = self._requests.spawn(_send, prefetch=False)
        # Increment report key when URL was succefully fetched.
        g.link_value(self._on_fetched)
        g.link_exception(self._on_exception)

    def log(self, msg, level=logging.INFO):
        "Log a message under ``level``, default to INFO."
        logging.log(level, msg)

    def start(self, argv=None, **kwargs):
        """Start/Launch crawling.

        Argument:
            argv: Command line arguments, default to ``sys.argv[1:]``.
            kwargs: Accept keys that should be part of the dictionary of
            :ref:`global configuration <global-configuration>`, which will
            override the default config values, the argument passed here have
            priority over the one read from the file in ``argv`` if they
            coincide.

        Command line argument:
            .. cmdoption:: --config=file.json

            The file.json configuration file should be in JSON format which
            will replace the default configuration that is taken from the
            :ref:`global configuration <global-configuration>`.

        """
        self.log('Start Crawling ...')
        self._configure(argv or sys.argv[1:], **kwargs)
        self._report['START TIME'] = datetime.now()
        error = None
        try:
            for page in self._website.pages:
                self._toprocess.put(page)
            gevent.spawn(self._loop).join()
        except:
            error = sys.exc_info()[1]
            self._report['EXCEPTIONS COUNTER'][error] += 1
            raise
        finally:
            self._finish(reason=error)

    def _loop(self):
        """Main loop that fetch every page and extract data from this later
        each action in an eventlet, until all pages are treated.

        """
        while 1:
            try:
                page = self._toprocess.get_nowait()
                if page is StopIteration:
                    break
            except Empty:
                # Wait until all requests and all extractors are done.
                if len(self._requests) == len(self._extractors) == 0:
                    break
                gevent.sleep()
            else:
                g = self._extractors.spawn(self._extract, page)
                g.link_exception(self._on_exception)
                gevent.sleep(self.__config['delay'])

    def _on_exception(self, greenlet):
        """Callback called when an exception is raised in greenlets that are
        spawned by this class, which include:

            * greenlet responsible of fetching URLs.
            * greenlet responsible of extracting data from HTML.
            * greenlet responsilbe of writing into pipelines.

        This method report the exception.

        """
        if self._exception_func:
            self._exception_func(greenlet)
        self._report['EXCEPTIONS COUNTER'] \
                    [greenlet.exception.__class__.__name__] += 1

    def _on_fetched(self, greenlet):
        """Callback called when an URL was fetched.

        This method report the fetched URL.

        """
        self.report['CRAWLED URLS'] += 1

    def _extract(self, page):
        """Extract data from a crawled web page.

        If the ``page`` contain links to follow this later will be added to
        the Queue of webpages to crawl.

        """
        # Extract data from this page.
        if page.toextract:
            try:
                page.extract()
            except ExtractionError:
                logging.error("Extraction from %s failed:", page.url)
                raise
            else:
                self.log(
                    'Scraped Data from %s:\n %s' % (page.url, page.data),
                    logging.DEBUG
                )
                self._report['EXTRACTED DATA'] += 1
                # Pass the page to pipelines after extraction.
                for pipeline in self._pipelines:
                    g = self._pipes.spawn(pipeline, page)
                    g.link_exception(self._on_exception)
        # Add new pages to crawl from links to follow.
        if page.tofollow:
            empty = True
            for new_page in page.follow_links():
                empty = False
                self.log('Follow: %s' % new_page.url, logging.DEBUG)
                self._add_to_queue(new_page)
            # Warn if no links was found in a page.
            if empty:
                self.log('No links to follow in %s' % page.url,logging.WARNING)

    def _add_to_queue(self, page):
        """Add a page to the queue to fetch."""
        if not self._takewhile(page):
            self.log(
                "Take while predicate return False for %s" % page.url,
                logging.DEBUG
            )
            self._toprocess.put(StopIteration)
        elif self._filter(page):
            self.log("Filter url %s" % page.url, logging.DEBUG)
        else:
            self._toprocess.put(page)

    def _finish(self, reason=None):
        """Clean up, set and show report."""
        self.log('Shutting down ...')
        try:
            # Join all the greenlets.
            self._extractors.join()
            self._requests.join()
            self._pipes.join()
            # Execute finish function after that all greenlet has finished.
            if self._finish_func:
                self._finish_func()
        finally:
            # Add report information.
            self._report['FINISH TIME'] = datetime.now()
            self._report['TOTAL TIME'] = str(
                self._report['FINISH TIME'] - self._report['START TIME']
            )
            if reason:
                self._report['SHUTDOWN REASON'] = reason
            self.log(self._report)

    @property
    def report(self):
        """Get execution report.

        The report contains the following fields:

            - CRAWLED URLS: count of crawled URLs.
            - EXTRACTED DATA: count of extracted data passed to pipelines.
            - EXCEPTIONS COUNTER: count number of exceptions raised.
            - START TIME: Date time when the crawler started.
            - FINISH TIME: Date time when the crawler finished.
            - TOTAL TIME: The total time spend crawling.
            - SHUTDOWN REASON: Reason why the crawler finished, i.e. show the
              exception that made the crawler stop if there is one, else show
              'FINISH CRAWLING' which mean the crawler finish normally.

        """
        return self._report


# Singleton default runner.
runner = _Runner()
