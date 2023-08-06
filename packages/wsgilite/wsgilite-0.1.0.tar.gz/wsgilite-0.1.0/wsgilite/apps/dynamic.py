from webob.dec import wsgify

from wsgilite.apps import static
from wsgilite.extras import restructured


class DynamicFile(object):
    raw = static.StaticFile
    rst = restructured.RstFile

    def __init__(self, path):
        self.path = path

    @wsgify
    def __call__(self, req):
        if req.GET.get('raw'):
            raw = self.raw(self.path)
            return req.get_response(raw)
        elif req.GET.get('rst'):
            print "DynamicFileApp --> rst", self.path
            rst = self.rst(self.path)
            return req.get_response(rst)
        else:
            raw = self.raw(self.path)
            return req.get_response(raw)


class DynamicDir(static.StaticDir):
    static_app = DynamicFile
