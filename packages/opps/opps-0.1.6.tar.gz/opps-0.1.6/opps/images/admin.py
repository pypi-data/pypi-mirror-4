# -*- coding: utf-8 -*-
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from django_thumbor import generate_url

from .models import Image
from opps.core.admin import PublishableAdmin


class ImagesAdmin(PublishableAdmin):
    prepopulated_fields = {"slug": ("title",)}
    list_display = ['image_thumb', 'title', 'date_available', 'published']
    list_filter = ['date_available', 'published']
    search_fields = ['title']
    raw_id_fields = ['source']
    readonly_fields = ['image_thumb']
    exclude = ('user',)

    fieldsets = (
        (_(u'Identification'), {
            'fields': ('site', 'title', 'slug', 'image')}),
        (_(u'Content'), {
            'fields': ('description', 'tags', 'source')}),
        (_(u'Publication'), {
            'classes': ('extrapretty'),
            'fields': ('published', 'date_available')}),
    )

    def image_thumb(self, obj):
        if obj.image:
            return u'<img width="60px" height="60px" src="{0}" />'.format(
                generate_url(obj.image.url, width=60, height=60))
        return _(u'No Image')
    image_thumb.short_description = _(u'Thumbnail')
    image_thumb.allow_tags = True

admin.site.register(Image, ImagesAdmin)
