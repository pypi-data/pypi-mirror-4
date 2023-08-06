import email
import mimetypes
import os
import urllib

import webob
from webob.dec import wsgify

from wsgilite.framework.method import HttpResource
from wsgilite.framework.method import httpmethod


__all__ = [
    'IndexFile',
    'StaticDir',
    'StaticFile',
]


class StaticFile(HttpResource):

    not_found = webob.Response(status=404)

    def __init__(self, path, content_type=None, content_encoding=None):
        self.path = path
        if content_type is None:
            content_type, content_encoding = mimetypes.guess_type(self.path)
        self.content_type = content_type
        self.content_encoding = content_encoding

    @httpmethod
    def HEAD(self, req):
        if not os.path.isfile(self.path):
            return self.not_found

        resp = webob.Response()
        resp.content_type = self.content_type
        resp.content_encoding = self.content_encoding

        file_info = os.stat(self.path)
        resp.date = email.utils.formatdate(file_info.st_mtime)
        return resp

    @httpmethod
    def GET(self, req):
        resp = req.get_response(self.HEAD)
        if 200 <= resp.status_int < 300:
            resp.body_file = open(self.path)
        return resp


class IndexFile(StaticFile):
    index_filename = 'index.html'

    @property
    def path(self):
        return os.path.join(self.real_path, self.index_filename)

    @path.setter
    def path(self, value):
        self.real_path = value


class StaticDir(object):
    """
    static file directory serving app.
    """
    static_app = StaticFile
    index_app = IndexFile
    not_found = webob.Response(status=404)

    def __init__(self, path='.'):
        self.path = path

    @wsgify
    def __call__(self, req):
        path = urllib.unquote_plus(req.path_info) or '/'
        # assert path.startswith('/')
        baseurl = os.path.normpath(path)
        abspath = os.path.join(self.path, baseurl[1:]).rstrip('/')

        if os.path.isfile(abspath):
            return req.get_response(self.static_app(abspath))  # (environ, start_response)

        elif os.path.isdir(abspath):
            return req.get_response(self.index_app(abspath, baseurl))  # (environ, start_response)

        else:
            return req.get_response(self.not_found)  # (environ, start_response)
