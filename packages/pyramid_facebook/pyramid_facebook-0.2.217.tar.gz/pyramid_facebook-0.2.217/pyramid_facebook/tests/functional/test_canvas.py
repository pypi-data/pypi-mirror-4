from __future__ import absolute_import

from pyramid_facebook.lib import js_redirect_tpl
from pyramid_facebook.tests.functional import TestView


class TestCanvas(TestView):
    def test_redirect_to_app(self):
        from pyramid_facebook.tests import conf
        namespace = conf["facebook.namespace"]

        res = self.app.get("/%s/" % namespace, status=200)
        self.assertEqual(
            js_redirect_tpl % {"location": "http://apps.facebook.com/%s" % namespace},
            res.body
        )
