"""
>>> from webob import Request, Response

"""
import copy
import mimetypes

from webob import exc
from webob.dec import wsgify


class vary(object):
    r"""

    decorator to support content negotiation.

        >>> from webob import Request, Response
        >>> import json, collections, csv, StringIO
        >>> class Foo(object):
        ...     FBBRow = collections.namedtuple('FBBRow', 'foo bar baz')
        ...     data = [FBBRow(1, 2, 3), FBBRow(4, 5, 6), FBBRow(7, 8, 9),]
        ...
        ...     @wsgify
        ...     def __call__(self, req):
        ...         return req.get_response(self.render(req))
        ...
        ...     @vary(default_media='text/html')
        ...     @wsgify
        ...     def render(self, req):
        ...         data = self.data
        ...         html = ("<html><head><title>%s</title></head>\n"
        ...                 "<body>\n%s\n</body></html>")
        ...         headings = "".join("<th>%s</th>" % label
        ...                            for label in self.FBBRow._fields)
        ...         tabledata = ["".join("<td>%d</td>" % field
        ...                              for field in row)
        ...                      for row in data]
        ...         table_rows = "\n".join("<tr>%s</tr>" % row
        ...                                for row in ([headings] + tabledata))
        ...         table = "<table>\n%s\n</table>" % table_rows
        ...         formatted = html % ("data!", table)
        ...         return formatted
        ...
        ...     @render(accept='text/csv')
        ...     @wsgify
        ...     def render(self, req):
        ...         data = self.data
        ...         outfile = StringIO.StringIO()
        ...         writer = csv.writer(outfile)
        ...         writer.writerow(self.FBBRow._fields)
        ...         writer.writerows(data)
        ...         return outfile.getvalue()
        ...
        ...     @render(accept='application/json')
        ...     @wsgify
        ...     def render(self, req):
        ...         data = self.data
        ...         return json.dumps(map(self.FBBRow._asdict, data))
        ...
        ...     @render(accept='application/javascript')
        ...     @wsgify
        ...     def render(self, req):
        ...         json_app = self.render.media['application/json']
        ...         jsondata = req.get_response(json_app)
        ...         try:
        ...             cb = req.GET['jsonp_callback']
        ...             resp = Response()
        ...             resp.text = u"%s(%s)" % (cb, jsondata.text)
        ...             return resp
        ...         except KeyError:
        ...             return jsondata
        ...

    When the client doesn't specify a content type, the default is used.

        >>> req = Request.blank('')
        >>> print req.get_response(Foo())
        200 OK
        Content-Type: text/html; charset=UTF-8
        Content-Length: 244
        Vary: accept
        <BLANKLINE>
        <html><head><title>data!</title></head>
        <body>
        <table>
        <tr><th>foo</th><th>bar</th><th>baz</th></tr>
        <tr><td>1</td><td>2</td><td>3</td></tr>
        <tr><td>4</td><td>5</td><td>6</td></tr>
        <tr><td>7</td><td>8</td><td>9</td></tr>
        </table>
        </body></html>

    Accept headers are honored:

        >>> req.accept = 'application/json'
        >>> print req.get_response(Foo())   # doctest: +NORMALIZE_WHITESPACE
        200 OK
        Content-Length: 96
        Content-Type: application/json; charset=UTF-8
        Vary: accept
        <BLANKLINE>
        [{"foo": 1, "bar": 2, "baz": 3},
         {"foo": 4, "bar": 5, "baz": 6},
         {"foo": 7, "bar": 8, "baz": 9}]
        >>> req.accept = 'text/csv'
        >>> print req.get_response(Foo())   # doctest: +NORMALIZE_WHITESPACE
        200 OK
        Content-Length: 34
        Content-Type: text/csv; charset=UTF-8
        Vary: accept
        <BLANKLINE>
        foo,bar,baz
        1,2,3
        4,5,6
        7,8,9

    There's nothing wrong with using one handler to support another:

        >>> req = Request.blank('?jsonp_callback=gotData')
        >>> req.accept = 'application/javascript'
        >>> print req.get_response(Foo())   # doctest: +NORMALIZE_WHITESPACE
        200 OK
        Content-Length: 105
        Content-Type: application/javascript; charset=UTF-8
        Vary: accept
        <BLANKLINE>
        gotData([{"foo": 1, "bar": 2, "baz": 3},
                 {"foo": 4, "bar": 5, "baz": 6},
                 {"foo": 7, "bar": 8, "baz": 9}])

    Real HTTP clients seldom set the HTTP Accept header correctly; standard
    practice is to use a filename or other media type distinguishing means in
    the url.

        >>> Request.blank('').get_response(Foo()).content_type
        'text/html'
        >>> Request.blank('?filename=data.csv').get_response(Foo()).content_type
        'text/csv'
        >>> Request.blank('?accept=application/json').get_response(Foo()).content_type
        'application/json'

    """

    def __init__(self, default_media='text/html'):
        self.default_media = default_media
        self.functions = {}

    def __call__(self, wrapped=None, accept=None):
        clone = copy.deepcopy(self)

        if accept is None:
            accept = clone.default_media

        def decorate(method):
            clone.functions[accept] = method
            return clone

        if wrapped:
            return decorate(wrapped)
        else:
            return decorate

    def __get__(self, instance, owner):
        # FIXME: This seems inefficient... oh well.
        if instance is None:
            return self
        vary_app = VaryResponse()
        vary_app.default_media = self.default_media
        for media, function in self.functions.iteritems():
            if hasattr(function, '__get__'):
                function = function.__get__(instance, owner)
            vary_app.media[media] = function
        return vary_app


class VaryResponse(object):
    """
    content negotiation capable wsgi app.  able to return client's choice of
    media types.  see vary for details.  End users should not need to make
    instances of or subclass this class
    """
    default_media = None

    @property
    def media(self):
        """
        a dict mapping uri's to wsgi applications.
        """
        try:
            collection = self.__collection
        except AttributeError:
            self.__collection = collection = {}
        return collection

    @wsgify
    def no_accept(self, req):
        """
        called when the request did not specify an 'Accept' header.  The
        request will be retried with accept of self.default_media
        """
        if req.GET.get('filename'):
            filename = req.GET['filename']
            accept = mimetypes.guess_type(filename)[0]
            if accept:
                req.accept = accept
                return
        try:
            default_media = self.default_media
        except AttributeError:
            return
        req.accept = default_media

    @wsgify
    def no_match(self, req):
        """
        """
        raise exc.HTTPPreconditionFailed

    def media_mismatch(self, req, match, resp):
        """
        called when the returned response did not satisfy the accepted media
        type.   If the resp has a media type of 'text/html', it will just be
        changed to the matched media type (the handler probably forgot to set
        it), and raises a HTTPPreconditionFailed otherwise.
        """
        # XXX
        if resp.content_type == 'text/html':
            resp.content_type = match
            return resp
        else:
            raise exc.HTTPPreconditionFailed

    @wsgify
    def __call__(self, req):
        #
        if req.GET.get('accept'):
            req.accept = req.GET['accept']
        if not req.accept or req.accept == '*/*':
            mimetype, _ = mimetypes.guess_type(req.path)
            if mimetype and mimetype in self.media:
                req.accept = mimetype
            else:
                self.no_accept(req)

        medias = self.media.keys()
        #medias.sort(key=(self.default_media.__ne__))
        match = req.accept.best_match(medias)
        # TODO: if no accept header (or generic accept:text/html), also
        # try using guess_type on the requested url.

        if match and req.accept.quality(match):
            resp = req.get_response(self.media[match])
            # "cheat a little...", match, resp.content_type
            if match != resp.content_type == 'text/html':
                resp.content_type = match
            elif not(req.accept.quality(resp.content_type)):
                resp = self.media_mismatch(req, match, resp)

        else:
            resp = req.get_response(self.no_match)

        # cache control:
        if self.media:
            resp.vary = (resp.vary or ()) + ('accept',)
        # TODO: localize
        #if self.locale:
        #    resp.vary = (resp.vary or ()) + ('accept-language',)

        return resp
