import webob
import os
import unittest
from wsgilite.apps import static

FIXTURES = os.path.join(os.path.dirname(__file__), 'fixtures')


class TestStatic(unittest.TestCase):
    def test_static_file(self):
        resp = webob.Request.blank('').get_response(static.StaticFile(os.path.join(FIXTURES, 'index.html')))
        self.assertEquals(resp.status_int, 200)
        self.assertEquals(resp.content_type, 'text/html')
