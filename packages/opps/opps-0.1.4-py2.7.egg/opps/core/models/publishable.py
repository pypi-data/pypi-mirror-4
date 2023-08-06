#!/usr/bin/env python
from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.contrib.sites.models import Site
from django.utils import timezone

from opps.core.models.date import Date


class PublishableManager(models.Manager):
    def all_published(self):
        return super(PublishableManager, self).get_query_set().filter(
            date_available__lte=timezone.now(), published=True)


class Publishable(Date):

    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    site = models.ForeignKey(Site, default=0)
    date_available = models.DateTimeField(_(u"Date available"),
                                          default=timezone.now, null=True)
    published = models.BooleanField(_(u"Published"), default=False)

    objects = PublishableManager()

    class Meta:
        abstract = True

    def is_published(self):
        return self.published and self.date_available <= timezone.now()
