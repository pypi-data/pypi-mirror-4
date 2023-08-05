# -*- coding: utf-8 -*-
#

from django.conf import settings


LOCAL_URL = getattr(settings, 'LOCAL_URL', 'http://127.0.0.1:8000')
STAGING_HOST = getattr(settings, 'DEPLOY_HOST', 'staging')
STAGING_PATH = getattr(settings, 'DEPLOY_PATH', '/home/web/ferrero/rocher.ferrero.sv-preview.de/site')
EXCLUDE_MEDIA = getattr(settings, 'EXCLUDE_MEDIA', ['admin', 'scss', 'release'])
GIT_SUPPORT = getattr(settings, 'GIT_SUPPORT', False)
