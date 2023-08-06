import collections
import datetime
import mimetypes
import os

import jinja2
import texttable


from webob.dec import wsgify

from wsgilite.apps import static
from wsgilite.extras.restructured import RstResource
from wsgilite.framework.method import HttpResource

fancy_index_item = collections.namedtuple('fancy_index_item', (
    'filename',
    'link_path',
    'isdir',
    'content_type',
    'content_encoding',
    'content_length',
    'date'))


@jinja2.contextfunction
def tabulate(ctx, template_name, items, header=None):
    template = ctx.environment.get_template(template_name)
    table = texttable.Texttable(0)
    if not header:
        header = template.blocks.keys()
    table.header(header)
    for item in items:
        item_ctx = template.new_context(ctx)
        item_ctx.vars['row'] = item
        row = []
        for field in header:
            row.append(''.join(template.blocks[field](item_ctx)))
        table.add_row(row)
    return table.draw()


ENV = jinja2.Environment(
    loader=jinja2.PackageLoader(__name__, 'templates'))

ENV.globals['tabulate'] = tabulate


class FancyIndex(RstResource, HttpResource):
    env = ENV
    show_hidden = False

    def __init__(self, fsdir, baseurl='/'):
        self.fsdir = fsdir
        self.baseurl = baseurl

    @wsgify
    def GET(self, req):
        return req.get_response(self.render)

    @RstResource.render(accept='text/x-rst')
    @wsgify
    def render(self, req):
        return self.env.get_template('index.rst').render(
            fsdir=self.fsdir,
            baseurl=req.script_name.rstrip('/') + self.baseurl,
            items=self.getdirlist())

    def getdirlist(self):
        #dirlist_path = os.path.join(self.path, self.baseurl)
        dirlist = [fancy_index_item(filename='.',
                                    link_path=self.baseurl,
                                    isdir=True,
                                    content_type=None,
                                    content_encoding=None,
                                    content_length=0,
                                    date=None,
                                    ),
                   fancy_index_item(filename='..',
                                    link_path=os.path.dirname(self.baseurl),
                                    isdir=True,
                                    content_type=None,
                                    content_encoding=None,
                                    content_length=0,
                                    date=None,
                                    ), ]
        for dirent in os.listdir(self.fsdir):
            if not self.show_hidden and dirent.startswith('.'):
                continue
            dirent_path = os.path.join(self.fsdir, dirent)
            content_type, content_encoding = mimetypes.guess_type(dirent)
            stat_info = os.stat(dirent_path)
            dirlist.append(fancy_index_item(filename=dirent,
                                            link_path='/'.join((self.baseurl.rstrip('/'), dirent)),
                                            isdir=os.path.isdir(dirent_path),
                                            content_type=content_type,
                                            content_encoding=content_encoding,
                                            content_length=stat_info.st_size,
                                            date=datetime.datetime.fromtimestamp(stat_info.st_mtime)))

        dirlist.sort()
        return dirlist


class FancyDir(static.StaticDir):
    index_app = FancyIndex
