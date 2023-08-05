# -*- coding: utf-8 -*-
#

from django_medusa.renderers import StaticSiteRenderer
from .models import RegisteredUrl


class ReleaseRenderer(StaticSiteRenderer):
    def get_paths(self):

        paths = []
        item_list = RegisteredUrl.objects.filter(checked=True).order_by('url')

        for item in item_list:
            paths.append(item.url)

        return paths

renderers = [ReleaseRenderer, ]
