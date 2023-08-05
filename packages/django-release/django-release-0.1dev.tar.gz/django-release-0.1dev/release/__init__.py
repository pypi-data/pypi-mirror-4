# -*- coding: utf-8 -*-
#

from django.db.models.signals import post_save
from .models import RegisteredUrl
from .tasks import ValidateURLs


def save_url_handler(sender, **kwargs):
    try:
        instance = kwargs.get('instance')
        url = instance.get_absolute_url()

        try:
            registeredurl = RegisteredUrl(url=url)
            registeredurl.save()
        except:
            pass

        ValidateURLs.delay()
    except:
        pass

post_save.connect(save_url_handler)
