from webob.dec import wsgify
from webob import Response


def set_httpmethod(wrapped):
    """
    inform HttpResource that the decorated function is a wsgi callable that
    represents a specific HTTP method.
    """
    wrapped._httpmethod = True
    return wrapped


class httpmethod(wsgify):
    """
    inform HttpResource that the decorated function takes a webob.Request and
    returns a wsgi callable (eg, returns ResponseEx instance) for a specific
    HTTP method.
    """
    _httpmethod = True


# TODO: implement OPTIONS;
class HttpResource(object):
    """
        >>> from webob import Request, Response
        >>> class HTCPTP(HttpResource):
        ...     @httpmethod
        ...     def BREW(self, req):
        ...         return Response("Putting the kettle on")
        ...     POST = BREW
        ...
        >>> print Request.blank("", method="BREW").get_response(HTCPTP())
        200 OK
        Content-Type: text/html; charset=UTF-8
        Content-Length: 21
        <BLANKLINE>
        Putting the kettle on
        >>> print Request.blank("", method="POST").get_response(HTCPTP())
        200 OK
        Content-Type: text/html; charset=UTF-8
        Content-Length: 21
        <BLANKLINE>
        Putting the kettle on
        >>> print Request.blank("", method="WHEN").get_response(HTCPTP())
        405 Method Not Allowed
        Content-Type: text/html; charset=UTF-8
        Content-Length: 0
        Allow: BREW, POST

    """
    @property
    def methods(self):
        """
        returns the list of httpmethods (by name) implemented for this
        resource.
        """
        _methods = []
        cls = type(self)
        for attr in dir(cls):
            if getattr(getattr(cls, attr), '_httpmethod', False):
                _methods.append(attr)
        return _methods

    def method_not_allowed(self, req):
        """
        Called when an HTTP method is specified in a request for which there is
        no defined httpmethod.  By default, this responds with a 405 Not
        Allowed response.
        """
        resp = Response(status=405)
        resp.allow = self.methods
        return resp

    @wsgify
    def __call__(self, req):
        if getattr(getattr(self, req.method, None), '_httpmethod', False):
            return getattr(self, req.method)
        try:
            super_call = super(HttpResource, self).__call__
        except AttributeError:
            return self.method_not_allowed(req)
        return super_call(req)
