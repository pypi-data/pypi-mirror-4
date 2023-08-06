import logging
from webob.dec import wsgify
from webob import Request
LOGGER = logging.getLogger(__name__)


def sqlalchemy_middlware(sessionfactory):
    def _wrapped(app):
        return SqlalchemyMiddleware(app, sessionfactory)
    return _wrapped


class SqlalchemyMiddleware(object):
    r"""
    A sqlalchemy session middlware.

    this package has no dependency on sqlalchemy or any database, it requires
    injection of a session factory (for instance, sqlalchemy.orm.sessionmaker).
    which has the side benefit of making it a little clearer what actually
    happens during each request, by substituting a mock session:

        >>> import minimock
        >>> from webob import Response
        >>> Session = minimock.Mock("Session")
        >>> Session.mock_returns = minimock.Mock("session")
        >>> @sqlalchemy_middlware(Session)
        ... @wsgify
        ... def app(req):
        ...     if req.GET.get('session'):
        ...         session = SqlalchemyMiddleware.get_session(req)
        ...     if req.GET.get('except'):
        ...         1/0
        ...     return Response(status=req.GET.get('status'))
        ...

    If the session is never requested, it doesn't get created either.

        >>> print Request.blank("").get_response(app)
        200 OK
        Content-Type: text/html; charset=UTF-8
        Content-Length: 0

    The session is closed at the end of the request (before consuming the
    returned app_iter)

        >>> print Request.blank("/?session=yes").get_response(app)
        Called Session()
        Called session.close()
        200 OK
        Content-Type: text/html; charset=UTF-8
        Content-Length: 0

    Errors propagate, but are trapped as they pass through the middlware for
    the purposes of cleaning up the session:

        >>> try:
        ...     print Request.blank("/?except=yes&session=yes") \
        ...                  .get_response(app)
        ... except ZeroDivisionError:
        ...     print "it died"
        ...
        Called Session()
        Called session.rollback()
        Called session.close()
        it died

    As before, if the session isn't used, then there's no session at all;  that
    goes for cleanup as well.

        >>> print Request.blank("/?except=yes").get_response(app)
        Traceback (most recent call last):
            1/0
        ZeroDivisionError: integer division or modulo by zero


    """

    # TODO: multi-database semantics
    #   change get_session(req) to get_session(req, "db-id") (optional)
    # TODO: autocommit on response (matches common expectations)

    def __init__(self, application, session_factory):
        self.application = application
        self.session_factory = session_factory

    @classmethod
    def get_session(cls, req=None, environ=None):
        """
        Create a new session and attach it to the supplied Request, or return
        the already attached session if it exists
        """
        if req is None:
            req = Request(environ)
        try:
            return req.sqlalchemy_middlware_session
        except AttributeError:
            pass
        self = req.sqlalchemy_middleware_instance
        req.sqlalchemy_middlware_session = session = self.session_factory()
        LOGGER.debug("sa.mw creating new session")
        return session

    @classmethod
    def rollback(cls, req=None, environ=None):
        """
        Roll back the current transaction on the supplied Request, or do
        nothing if there is no current session.
        """
        if req is None:
            req = Request(environ)
        try:
            session = req.sqlalchemy_middlware_session
        except AttributeError:
            LOGGER.debug("sa.mw no session to rollback")
            return
        LOGGER.debug("sa.mw session.rollback")
        session.rollback()

    @classmethod
    def close(cls, req=None, environ=None):
        """
        Close the current transaction on the supplied Request, or do
        nothing if there is no current session.
        """
        if req is None:
            req = Request(environ)
        try:
            session = req.sqlalchemy_middlware_session
        except AttributeError:
            LOGGER.debug("sa.mw no session to close")
            return
        LOGGER.debug("sa.mw session.close")
        session.close()
        del req.sqlalchemy_middlware_session

    @wsgify
    def __call__(self, req):
        req.sqlalchemy_middleware_instance = self
        app = self.application
        try:
            resp = req.get_response(app)
            return resp
        except:
            LOGGER.debug("sa.mw rollback forced on exception in %r()",
                         app, exc_info=True)
            self.rollback(req)
            raise
        finally:
            self.close(req)
            del req.sqlalchemy_middleware_instance
