# (c) 2005 Ian Bicking and contributors;
# written for Paste (http://pythonpaste.org)
# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license.php
"""
Map URL prefixes to WSGI applications.  See ``URLMap``
"""

from ginsfsm.compat import escape
import re

__all__ = ['URLMap']

class DictMixin:
    # Mixin defining all dictionary methods for classes that already have
    # a minimum dictionary interface including getitem, setitem, delitem,
    # and keys. Without knowledge of the subclass constructor, the mixin
    # does not define __init__() or copy().  In addition to the four base
    # methods, progressively more efficiency comes with defining
    # __contains__(), __iter__(), and iteritems().

    # second level definitions support higher levels
    def __iter__(self):
        for k in self.keys():
            yield k
    def has_key(self, key):
        try:
            self[key]
        except KeyError:
            return False
        return True
    def __contains__(self, key):
        return self.has_key(key)

    # third level takes advantage of second level definitions
    def iteritems(self):
        for k in self:
            yield (k, self[k])
    def iterkeys(self):
        return self.__iter__()

    # fourth level uses definitions from lower levels
    def itervalues(self):
        for _, v in self.iteritems():
            yield v
    def values(self):
        return [v for _, v in self.iteritems()]
    def items(self):
        return list(self.iteritems())
    def clear(self):
        for key in self.keys():
            del self[key]
    def setdefault(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            self[key] = default
        return default
    def pop(self, key, *args):
        if len(args) > 1:
            raise TypeError("pop expected at most 2 arguments, got "\
                              + repr(1 + len(args)))
        try:
            value = self[key]
        except KeyError:
            if args:
                return args[0]
            raise
        del self[key]
        return value
    def popitem(self):
        try:
            k, v = self.iteritems().next()
        except StopIteration:
            raise KeyError('container is empty')
        del self[k]
        return (k, v)
    def update(self, other=None, **kwargs):
        # Make progressively weaker assumptions about "other"
        if other is None:
            pass
        elif hasattr(other, 'iteritems'):  # iteritems saves memory and lookups
            for k, v in other.iteritems():
                self[k] = v
        elif hasattr(other, 'keys'):
            for k in other.keys():
                self[k] = other[k]
        else:
            for k, v in other:
                self[k] = v
        if kwargs:
            self.update(kwargs)
    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default
    def __repr__(self):
        return repr(dict(self.iteritems()))
    def __cmp__(self, other):
        if other is None:
            return 1
        if isinstance(other, DictMixin):
            other = dict(other.iteritems())
        return cmp(dict(self.iteritems()), other)
    def __len__(self):
        return len(self.keys())


def urlmap_factory(loader, global_conf, **local_conf):
    """
        # TODO: check
        [composite:urlmap]
        use = call:ginsfsm.protocols.wsgi.common.urlmap:urlmap_factory
        / = home
        /blog = blog
        /wiki = wiki

        [app:home]
        use = call:ginsfsm.examples.wsgi.simple_wsgi_server:paste_app_factory

        [app:blog]
        use = call:ginsfsm.examples.wsgi.simple_wsgi_server:paste_app_factory

        [app:wiki]
        use = call:ginsfsm.examples.wsgi.simple_wsgi_server:paste_app_factory
    """
    if 'not_found_app' in local_conf:
        not_found_app = local_conf.pop('not_found_app')
    else:
        not_found_app = global_conf.get('not_found_app')
    if not_found_app:
        not_found_app = loader.get_app(not_found_app, global_conf=global_conf)
    urlmap = URLMap(not_found_app=not_found_app)
    for path, app_name in local_conf.items():
        path = parse_path_expression(path)
        app = loader.get_app(app_name, global_conf=global_conf)
        urlmap[path] = app
    return urlmap


def parse_path_expression(path):
    """
    Parses a path expression like 'domain foobar.com port 20 /' or
    just '/foobar' for a path alone.  Returns as an address that
    URLMap likes.
    """
    parts = path.split()
    domain = port = path = None
    while parts:
        if parts[0] == 'domain':
            parts.pop(0)
            if not parts:
                raise ValueError(
                    "'domain' must be followed with a domain name")
            if domain:
                raise ValueError("'domain' given twice")
            domain = parts.pop(0)
        elif parts[0] == 'port':
            parts.pop(0)
            if not parts:
                raise ValueError("'port' must be followed with a port number")
            if port:
                raise ValueError("'port' given twice")
            port = parts.pop(0)
        else:
            if path:
                raise ValueError("more than one path given (have %r, got %r)"
                                 % (path, parts[0]))
            path = parts.pop(0)
    s = ''
    if domain:
        s = 'http://%s' % domain
    if port:
        if not domain:
            raise ValueError("If you give a port, you must also give a domain")
        s += ':' + port
    if path:
        if s:
            s += '/'
        s += path
    return s


class URLMap(DictMixin):

    """
    URLMap instances are dictionary-like object that dispatch to one
    of several applications based on the URL.

    The dictionary keys are URLs to match (like
    ``PATH_INFO.startswith(url)``), and the values are applications to
    dispatch to.  URLs are matched most-specific-first, i.e., longest
    URL first.  The ``SCRIPT_NAME`` and ``PATH_INFO`` environmental
    variables are adjusted to indicate the new context.

    URLs can also include domains, like ``http://blah.com/foo``, or as
    tuples ``('blah.com', '/foo')``.  This will match domain names; without
    the ``http://domain`` or with a domain of ``None`` any domain will be
    matched (so long as no other explicit domain matches).  """

    def __init__(self, not_found_app=None):
        self.applications = []
        if not not_found_app:
            not_found_app = self.not_found_app
        self.not_found_application = not_found_app

    norm_url_re = re.compile('//+')
    domain_url_re = re.compile('^(http|https)://')

    def not_found_app(self, environ, start_response):
        # TODO: must change to ginsfsm http response!
        mapper = environ.get('paste.urlmap_object')
        if mapper:
            matches = [p for p, a in mapper.applications]
            extra = 'defined apps: %s' % (
                ',\n  '.join(list(map(repr, matches))))
        else:
            extra = ''
        extra += '\nSCRIPT_NAME: %r' % environ.get('SCRIPT_NAME')
        extra += '\nPATH_INFO: %r' % environ.get('PATH_INFO')
        extra += '\nHTTP_HOST: %r' % environ.get('HTTP_HOST')
        # NotFound('The resource could not be found.')
        # TODO: eliminate paste dependency
        from paste import httpexceptions
        app = httpexceptions.HTTPNotFound(
            environ['PATH_INFO'],
            comment=escape(extra)).wsgi_application
        return app(environ, start_response)

    def normalize_url(self, url, trim=True):
        if isinstance(url, (list, tuple)):
            domain = url[0]
            url = self.normalize_url(url[1])[1]
            return domain, url
        assert (not url or url.startswith('/')
                or self.domain_url_re.search(url)), (
            "URL fragments must start with / or http:// (you gave %r)" % url)
        match = self.domain_url_re.search(url)
        if match:
            url = url[match.end():]
            if '/' in url:
                domain, url = url.split('/', 1)
                url = '/' + url
            else:
                domain, url = url, ''
        else:
            domain = None
        url = self.norm_url_re.sub('/', url)
        if trim:
            url = url.rstrip('/')
        return domain, url

    def sort_apps(self):
        """
        Make sure applications are sorted with longest URLs first
        """
        def key(app_desc):
            (domain, url), app = app_desc
            if not domain:
                # Make sure empty domains sort last:
                return '\xff', -len(url)
            else:
                return domain, -len(url)
        apps = [(key(desc), desc) for desc in self.applications]
        apps.sort()
        self.applications = [desc for (sortable, desc) in apps]

    def __setitem__(self, url, app):
        if app is None:
            try:
                del self[url]
            except KeyError:
                pass
            return
        dom_url = self.normalize_url(url)
        if dom_url in self:
            del self[dom_url]
        self.applications.append((dom_url, app))
        self.sort_apps()

    def __getitem__(self, url):
        dom_url = self.normalize_url(url)
        for app_url, app in self.applications:
            if app_url == dom_url:
                return app
        raise KeyError(
            "No application with the url %r (domain: %r; existing: %s)"
            % (url[1], url[0] or '*', self.applications))

    def __delitem__(self, url):
        url = self.normalize_url(url)
        for app_url, app in self.applications:
            if app_url == url:
                self.applications.remove((app_url, app))
                break
        else:
            raise KeyError(
                "No application with the url %r" % (url,))

    def keys(self):
        return [app_url for app_url, app in self.applications]

    def __call__(self, environ, start_response):
        host = environ.get('HTTP_HOST', environ.get('SERVER_NAME')).lower()
        if ':' in host:
            host, port = host.split(':', 1)
        else:
            if environ['wsgi.url_scheme'] == 'http':
                port = '80'
            else:
                port = '443'
        path_info = environ.get('PATH_INFO')
        path_info = self.normalize_url(path_info, False)[1]
        for (domain, app_url), app in self.applications:
            if domain and domain != host and domain != host + ':' + port:
                continue
            if (path_info == app_url
                or path_info.startswith(app_url + '/')):
                environ['SCRIPT_NAME'] += app_url
                environ['PATH_INFO'] = path_info[len(app_url):]
                return app(environ, start_response)
        environ['paste.urlmap_object'] = self
        return self.not_found_application(environ, start_response)
