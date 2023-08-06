import time
from django.db import models
from django.contrib.sites.models import Site
from django.utils import timezone
from django.core.cache import cache

import settings


class LastSeenManager(models.Manager):
    def seen(self, user, module=settings.LAST_SEEN_DEFAULT_MODULE):
        args = {
            'user': user,
            'site': Site.objects.get_current(),
            'module': module,
        }
        updated = self.filter(**args).update(last_seen=timezone.now())
        if not updated:
            self.create(**args)

    def when(self, user, module=None, site=None):
        args = {'user': user}
        if module:
            args['module'] = module
        if site:
            args['site'] = site
        return self.filter(**args).latest('last_seen').last_seen


class LastSeen(models.Model):
    site = models.ForeignKey(Site)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    module = models.CharField(default=settings.LAST_SEEN_DEFAULT_MODULE, max_length=20)
    last_seen = models.DateTimeField(default=timezone.now)

    objects = LastSeenManager()

    class Meta:
        unique_together = (('user', 'site', 'module'),)
        ordering = ('-last_seen',)

    def __unicode__(self):
        return u"%s on %s" % (self.user, self.last_seen)


def user_seen(user, module=settings.LAST_SEEN_DEFAULT_MODULE):
    # compute limit to update db
    cache_key = "last_seen:%s:%s" % (module, user.pk)
    limit = time.time() - settings.LAST_SEEN_INTERVAL
    seen = cache.get(cache_key)
    if not seen or seen < limit:
        # mark the database and the cache
        LastSeen.objects.seen(user, module=module)
        cache.set(cache_key, time.time())
