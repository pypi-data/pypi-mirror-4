import datetime
import mock
import time
from django.test import TestCase
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.cache import cache

from last_seen.models import LastSeen, user_seen, clear_interval
from last_seen import settings
from last_seen import middleware


class TestLastSeenModel(TestCase):

    def test_unicode(self):
        user = User(username='testuser')
        ts = datetime.datetime(2013, 1, 1, 2, 3, 4)
        seen = LastSeen(user=user, last_seen=ts)
        self.assertIn('testuser', unicode(seen))
        self.assertIn('2013-01-01 02:03:04', unicode(seen))


class TestLastSeenManager(TestCase):

    @mock.patch('last_seen.models.LastSeen.objects.create', autospec=True)
    @mock.patch('last_seen.models.LastSeen.objects.filter', autospec=True)
    def test_seen(self, filter, create):
        user = User(username='testuser')
        filter.return_value.update.return_value = 1

        LastSeen.objects.seen(user=user)

        filter.assert_called_with(user=user,
                module=settings.LAST_SEEN_DEFAULT_MODULE,
                site=Site.objects.get_current())
        self.assertFalse(create.called)

    @mock.patch('last_seen.models.LastSeen.objects.create', autospec=True)
    @mock.patch('last_seen.models.LastSeen.objects.filter', autospec=True)
    def test_seen_no_default(self, filter, create):
        user = User(username='testuser')
        site = Site(pk=2)
        filter.return_value.update.return_value = 1

        LastSeen.objects.seen(user=user, site=site, module="test")

        filter.assert_called_with(user=user, module="test", site=site)
        self.assertFalse(create.called)

    @mock.patch('last_seen.models.LastSeen.objects.create', autospec=True)
    @mock.patch('last_seen.models.LastSeen.objects.filter', autospec=True)
    def test_seen_create(self, filter, create):
        user = User(username='testuser')
        filter.return_value.update.return_value = 0

        LastSeen.objects.seen(user=user)

        filter.assert_called_with(user=user,
                module=settings.LAST_SEEN_DEFAULT_MODULE,
                site=Site.objects.get_current())
        create.assert_called_with(user=user,
                module=settings.LAST_SEEN_DEFAULT_MODULE,
                site=Site.objects.get_current())

    def test_when_non_existent(self):
        user = User(username='testuser', pk=1)
        self.assertRaises(LastSeen.DoesNotExist, LastSeen.objects.when, user)

    @mock.patch('last_seen.models.LastSeen.objects.filter', autospec=True)
    def test_seen_defaults(self, filter):
        user = User(username='testuser')
        LastSeen.objects.when(user=user)

        filter.assert_called_with(user=user)

    @mock.patch('last_seen.models.LastSeen.objects.filter', autospec=True)
    def test_seen_module(self, filter):
        user = User(username='testuser')
        LastSeen.objects.when(user=user, module='mod')

        filter.assert_called_with(user=user, module='mod')

    @mock.patch('last_seen.models.LastSeen.objects.filter', autospec=True)
    def test_seen_site(self, filter):
        user = User(username='testuser')
        site = Site()
        LastSeen.objects.when(user=user, site=site)

        filter.assert_called_with(user=user, site=site)


class TestUserSeen(TestCase):

    @mock.patch('last_seen.models.LastSeen.objects.seen', autospec=True)
    def test_user_seen(self, seen):
        user = User(username='testuser', pk=1)
        user_seen(user)
        site = Site.objects.get_current()
        seen.assert_called_with(user, module=settings.LAST_SEEN_DEFAULT_MODULE,
                                site=site)

    @mock.patch('last_seen.models.LastSeen.objects.seen', autospec=True)
    def test_user_seen_no_default(self, seen):
        user = User(username='testuser', pk=1)
        site = Site(pk=2)
        user_seen(user, module="test", site=site)
        seen.assert_called_with(user, module="test", site=site)

    @mock.patch('last_seen.models.LastSeen.objects.seen', autospec=True)
    def test_user_seen_cached(self, seen):
        user = User(username='testuser', pk=1)
        module = 'test_mod'
        cache.set("last_seen:%s:%s" % (module, user.pk), time.time())
        user_seen(user, module=module)
        self.assertFalse(seen.called)

    @mock.patch('last_seen.models.LastSeen.objects.seen', autospec=True)
    def test_user_seen_cache_expired(self, seen):
        user = User(username='testuser', pk=1)
        module = 'test_mod'
        cache.set("last_seen:%s:%s" % (module, user.pk),
                time.time() - (2 * settings.LAST_SEEN_INTERVAL))
        user_seen(user, module=module)
        site = Site.objects.get_current()
        seen.assert_called_with(user, module=module, site=site)


class TestClearInterval(TestCase):

    @mock.patch('last_seen.models.LastSeen.objects.filter', autospec=True)
    @mock.patch('last_seen.models.cache', autospec=True)
    def test_clear_interval(self, cache, filter):
        site = Site.objects.get_current()
        user = User(username='testuser', pk=1)
        ls1 = LastSeen(user=user, module="mod1", site=site)
        ls2 = LastSeen(user=user, module="mod2", site=site)
        filter.return_value = [ls1, ls2]

        clear_interval(user)

        filter.assert_called_with(user=user)
        expected = ['last_seen:1:mod1:1', 'last_seen:1:mod2:1']
        cache.delete_many.assert_called_with(expected)

    @mock.patch('last_seen.models.LastSeen.objects.filter', autospec=True)
    @mock.patch('last_seen.models.cache', autospec=True)
    def test_clear_interval_none(self, cache, filter):
        user = User(username='testuser', pk=1)
        filter.return_value = []

        clear_interval(user)

        filter.assert_called_with(user=user)
        self.assertFalse(cache.delete_many.called)


class TestMiddleware(TestCase):

    middleware = middleware.LastSeenMiddleware()

    @mock.patch('last_seen.middleware.user_seen', autospec=True)
    def test_process_request(self, user_seen):
        request = mock.Mock()
        request.user.is_authenticated.return_value = False
        self.middleware.process_request(request)
        self.assertFalse(user_seen.called)

    @mock.patch('last_seen.middleware.user_seen', autospec=True)
    def test_process_request_auth(self, user_seen):
        request = mock.Mock()
        request.user.is_authenticated.return_value = True
        self.middleware.process_request(request)
        user_seen.assert_called_with(request.user)
