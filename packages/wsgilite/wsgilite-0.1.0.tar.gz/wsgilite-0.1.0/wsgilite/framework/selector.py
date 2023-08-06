from webob import exc
import wsgiref.util


def all_sub_paths(environ):
    """
    return a list containing the pairs of script_name and path_info that the
    supplied environ can contain, from shortest script name to longest.  Note
    this will also include the 'root', with empty script_name.  the existing
    environ is not modified.

    >>> all_sub_paths({'PATH_INFO': '/foo/bar'})
    [('', '/foo/bar'), ('/foo', '/bar'), ('/foo/bar', '')]
    >>> all_sub_paths({'PATH_INFO': '/foo/bar/'})
    [('', '/foo/bar/'), ('/foo', '/bar/'), ('/foo/bar', '/'), ('/foo/bar/', '')]
    >>> all_sub_paths({'PATH_INFO': '/foo//bar'})
    [('', '/foo//bar'), ('/foo', '/bar'), ('/foo/bar', '')]

    """
    test_environ = {'SCRIPT_NAME': '',
                    'PATH_INFO': environ['PATH_INFO']}
    script_names = []
    script_names.append((test_environ['SCRIPT_NAME'],
                         test_environ['PATH_INFO']))
    while wsgiref.util.shift_path_info(test_environ) is not None:
        script_names.append((test_environ['SCRIPT_NAME'],
                             test_environ['PATH_INFO']))
    return script_names


class ScriptCollection(object):
    r"""
    organize a pile of applications by "script_name".

    Mount some applications at assorted uri's

        >>> from webob import Request, Response
        >>> collection = ScriptCollection.from_dict(
        ...     {'': Response(body="Welcome"),
        ...      '/beer': exc.HTTPUnauthorized("21 and Over"),
        ...      '/foo/bar/baz/long/path': Response("That was tough!")})

    matching names are dispatched to the named app

        >>> print Request.blank("").get_response(collection)
        200 OK
        Content-Type: text/html; charset=UTF-8
        Content-Length: 7
        <BLANKLINE>
        Welcome
        >>> print Request.blank("/").get_response(collection)
        200 OK
        Content-Type: text/html; charset=UTF-8
        Content-Length: 7
        <BLANKLINE>
        Welcome
        >>> print Request.blank("/beer").get_response(collection)
        ...     # doctest: +NORMALIZE_WHITESPACE +ELLIPSIS
        401 Unauthorized
        Content-Length: 264
        Content-Type: text/plain; charset=UTF-8
        <BLANKLINE>
        401 Unauthorized
        <BLANKLINE>
        This server could not verify ...
        <BLANKLINE>
        21 and Over
        >>> print Request.blank("/foo/bar").get_response(collection)
        200 OK
        Content-Type: text/html; charset=UTF-8
        Content-Length: 7
        <BLANKLINE>
        Welcome
        >>> print Request.blank("/foo/bar/baz/long/path/quux"
        ...                     ).get_response(collection)
        200 OK
        Content-Type: text/html; charset=UTF-8
        Content-Length: 15
        <BLANKLINE>
        That was tough!

    """

    @classmethod
    def from_dict(cls, apps):
        self = cls()
        for script_name, app in apps.iteritems():
            self.scripts[script_name] = app
        return self

    @property
    def scripts(self):
        """
        a dict mapping uri's to wsgi applications.
        """
        try:
            collection = self.__collection
        except AttributeError:
            self.__collection = collection = {}
        return collection

    def __call__(self, environ, start_response):
        for (script_name, path_info) in reversed(all_sub_paths(environ)):
            if script_name in self.scripts:
                environ['SCRIPT_NAME'] += script_name
                environ['PATH_INFO'] = path_info
                return self.scripts[script_name](environ, start_response)
        try:
            super_call = super(ScriptCollection, self).__call__
        except AttributeError:
            return exc.HTTPNotFound()(environ, start_response)
        return super_call(environ, start_response)
