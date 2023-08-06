from webob.dec import wsgify
from webob import Response


@wsgify
def echo_app(req):
    resp = Response(body=str(req))
    resp.content_type = 'text/plain'
    return resp


@wsgify
def echo_status(req):
    status = req.path_info.lstrip('/')
    resp = Response()
    resp.status = status
    return resp
