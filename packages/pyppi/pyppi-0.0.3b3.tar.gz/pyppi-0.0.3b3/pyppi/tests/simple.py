from django_webtest import WebTest
from guardian.utils import get_anonymous_user
from pyppi.models import KnownHost
from pyppi.tests.base import BaseTestMixin
from pyppi.tests.download import BasicAuthMixin


class AnonymousDownloadTestCase(BasicAuthMixin, BaseTestMixin, WebTest):

    def setUp(self):
        super(AnonymousDownloadTestCase, self).setUp()
        self.user = get_anonymous_user()

    def test_public(self):
        target = '/simple/%s/' % self.package.name
        host = KnownHost.objects.create(ip='127.0.0.1', description='localhost')
        host.packages.add(self.package)
        self.app.get(target)

    def test_simple(self):
        target = '/simple/'
        with self.basic_auth():
            res = self.app.get(target, 'anonymous')
            self.assertNotContains(res, 'package1')
            self.assertContains(res, 'protected_package')

            res = res.click('public_package')
            res = res.click('public_package-1.0.tar.gz')
            self.assertEqual(res['Content-Type'], 'application/x-tar')
