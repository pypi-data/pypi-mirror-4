# -*- coding: utf-8 -*-
#

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _


class Release(models.Model):
    STATUS_CHOICES = (
        (0, _('Pending')),
        (1, _('In progress')),
        (2, _('Finish')),
        (3, _('Error')),
    )

    user = models.ForeignKey(User, verbose_name=_('User'))
    version = models.CharField(_('Version'), max_length=50, blank=True)
    archive = models.FileField(_('Archive'), upload_to='release/archives/',
                               blank=True)
    excluded_media = models.CharField(_('Excluded media'), max_length=50, blank=True, help_text=_('Comma seperated list (e.g. cms,admin,etc.)'))
    timestamp = models.CharField(_('Timestamp'), max_length=100, blank=True)
    date_start = models.DateTimeField(_('Date start'), auto_now_add=True)
    date_end = models.DateTimeField(_('Date end'), auto_now=True)
    status = models.IntegerField('Status', default=0, choices=STATUS_CHOICES)
    done = models.BooleanField(_('Done'), default=False)
    log = models.TextField(_('Log'), blank=True)

    git_commit = models.CharField(_('HEAD Commit'), max_length=150, blank=True)
    git_commit_m = models.TextField(_('HEAD Commit Message'), blank=True)

    class Meta:
        app_label = 'release'
        verbose_name = _('Release')
        verbose_name_plural = _('Releases')

    def __unicode__(self):
        return u'%s' % (self.timestamp)

    def delete(self, *args, **kwargs):
        try:
            storage, path = self.archive.storage, self.archive.path
        except:
            pass

        super(Release, self).delete(*args, **kwargs)

        try:
            storage.delete(path)
        except:
            pass


class DeploymentHost(models.Model):
    TYPE_CHOICES = (
        (0, 'Local'),
        (1, 'FTP'),
        (2, 'SSH'),
    )

    AUTHTYPE_CHOICES = (
        (0, _('Password')),
        (1, _('Public/Private Key')),
    )

    title = models.CharField(_('Title'), max_length=100)
    url = models.URLField(_('URL'), blank=True, help_text=_('URL to view the deployed result.'))
    type = models.IntegerField(_('Type'), choices=TYPE_CHOICES)
    host = models.CharField(_('Server'), max_length=80, blank=True, help_text=_('For example ssh.servername.com.'))
    user = models.CharField(_('Username'), max_length=80, blank=True)
    path = models.CharField(_('Path'), max_length=255, help_text=_('Please enter the parent directory of the target directory.'))
    authtype = models.IntegerField(_('Authentication type'),
                                   choices=AUTHTYPE_CHOICES,
                                   blank=True, null=True)
    password = models.CharField(_('Password'), max_length=80, blank=True)
    keypath = models.CharField(_('Keyfile path'), max_length=255, blank=True, help_text=_('Must be an absolute path.'))

    class Meta:
        app_label = 'release'
        verbose_name = _('Deployment host')
        verbose_name_plural = _('Deployment hosts')

    def __unicode__(self):
        return u'%s (%s)' % (self.title, self.get_type_display())


class RegisteredUrl(models.Model):
    STATUS_CHOICES = (
        (0, _('Wait for check')),
        (1, _('Checked')),
        (2, _('checking ...')),
    )

    site = models.CharField(_('Pagetitle'), max_length=255, blank=True)
    url = models.CharField('URL', max_length=255, unique=True)
    status = models.IntegerField('Status', default=0, choices=STATUS_CHOICES)
    checked = models.BooleanField(_('Valid'), default=False)

    class Meta:
        app_label = 'release'
        verbose_name = _('Registered URL')
        verbose_name_plural = _('Registered URLs')

    def __unicode__(self):
        return u'%s' % (self.url)
