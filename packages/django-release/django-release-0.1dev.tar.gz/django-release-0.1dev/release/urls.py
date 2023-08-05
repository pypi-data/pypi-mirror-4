# -*- coding: utf-8 -*-
#

from django.conf.urls import patterns, url


urlpatterns = patterns('release.views',

                       url(r'^admin/release/release/deploy/(?P<release_id>\d+)/$',
                       'deploy',
                       name='release_deploy'),

                       url(r'^admin/release/registeredurl/validate/$',
                       'validateurls',
                       name='release_validateurls'),
                       )
