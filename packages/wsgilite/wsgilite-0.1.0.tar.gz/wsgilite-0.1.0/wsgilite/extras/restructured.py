import os
import email

import docutils.core
import webob

from webob import exc
from webob.dec import wsgify


#from wsgilite.framework.method import HttpResource
from wsgilite.framework.cn import vary


class RstResource(object):
    r"""

    convert a resource in reStructuredText (a-la docutils) into any of a
    variety of other, useful formats.

    To use this class, you must provide an variant of the `render()` method for
    the `text/x-rst` media type, (the rStructuredText mime type).  which
    roughly looks like

    >>> import textwrap
    >>> class RstTestResource(RstResource):
    ...     document = textwrap.dedent('''
    ...     Hello World
    ...     ===========
    ...
    ...     - foo
    ...     - bar
    ...     - baz
    ...     ''').strip()
    ...
    ...     @RstResource.render(accept='text/x-rst')
    ...     @wsgify
    ...     def render(self, req):
    ...         return webob.Response(self.document)

    """

    @wsgify
    def __call__(self, req):
        print "RstResource --> render"
        return req.get_response(self.render(req))

    @vary(default_media='text/html')
    @wsgify
    def render(self, req):
        # obtain the reStructuredText version:
        print "RstResource.render --> text/x-rst"
        rstresponse = req.get_response(self.render.media['text/x-rst'])
        rst = rstresponse.text
        return webob.Response(docutils.core.publish_string(rst, writer_name='html'))


#FIXME: this repeats some of the stuff in static.StaticFile...
class RstFile(RstResource):
    def __init__(self, path):
        self.path = path

    @RstResource.render(accept='text/x-rst')
    @wsgify
    def render(self, req):
        if not os.path.isfile(self.path):
            raise exc.HTTPNotFound

        resp = webob.Response()
        resp.content_type = 'text/x-rst'

        file_info = os.stat(self.path)
        resp.date = email.utils.formatdate(file_info.st_mtime)
        resp.body_file = open(self.path)
        return resp
