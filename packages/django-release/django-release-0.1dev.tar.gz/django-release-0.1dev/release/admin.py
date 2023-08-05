# -*- coding: utf-8 -*-
#

from django.contrib import admin
from django.contrib import messages
from django.conf import settings
from release.models import *
from .tasks import *
from git import *
from django.utils.translation import ugettext as _
from .settings import GIT_SUPPORT


def delete_releases(modeladmin, request, queryset):
    for release in queryset:
        release.delete()
    messages.success(request, 'Die ausgewählten Releases wurden erfolgreich gelöscht.')
delete_releases.short_description = "Ausgewählte Releases löschen"


class ReleaseAdmin(admin.ModelAdmin):
    exclude = ('user', 'status', 'done', 'archive', 'timestamp',)
    list_display = ('timestamp',
                    'date_start',
                    'date_end',
                    'user_name',
                    'archivelink',
                    'deploylink',
                    'coloredstatus',
                    'loader',)
    list_filter = ('user', 'status', 'done',)
    fieldsets = (
        (None, {
            'fields': ('version', 'excluded_media',)
        }),
        (_('Versioning'), {
            'fields': ('git_commit', 'git_commit_m',),
            'classes': ('collapse',)
        }),
        ('Log', {
            'fields': ('log',),
            'classes': ('collapse',)
        }),
    )
    ordering = ('-date_start',)
    change_list_template = 'admin/release/release/change_list.html'
    actions = [delete_releases]
    readonly_fields = ('log',)

    def user_name(self, instance):
        if instance.user.get_full_name():
            return u'%s' % (instance.user.get_full_name())
        else:
            return u'%s' % (instance.user.username)
    user_name.short_description = _('User')

    def archivelink(self, instance):
        if instance.archive:
            return u'<a href="%s" target="_blank">Download</a>' % (instance.archive.url)
        else:
            return u'N/A'
    archivelink.short_description = _('Archive')
    archivelink.allow_tags = True

    def deploylink(self, instance):
        if instance.done:
            return u'<a href="/admin/release/release/deploy/%s/">Deploy</a>' % (instance.id)
        else:
            return u'N/A'
    deploylink.short_description = 'Staging'
    deploylink.allow_tags = True

    def coloredstatus(self, instance):
        if instance.status == 3:
            color = '#F00'
        elif instance.status == 2:
            color = 'green'
        else:
            color = '#FACC2E'

        return u'<span style="color:%s;">%s</span>' % (color, instance.STATUS_CHOICES[instance.status][1])
    coloredstatus.short_description = 'Status'
    coloredstatus.allow_tags = True

    def loader(self, instance):
        if instance.status == 1:
            return u'<div style="width: 20px; text-align: center;"><img src="/static/release/img/ajax-loader.gif" width="12" height="12" /></div>'
        else:
            return u'<div style="width: 20px;"></div>'
    loader.short_description = ''
    loader.allow_tags = True

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        obj.save()

        if not obj.done:
            MakeRelease.delay(obj)

    def get_form(self, request, obj=None, **kwargs):
        form = super(ReleaseAdmin, self).get_form(request, obj=None, **kwargs)

        if GIT_SUPPORT:
            repo = Repo(settings.PROJECT_DIR)
            head_commit = repo.head.commit
            form.base_fields['git_commit'].initial = head_commit
            form.base_fields['git_commit_m'].initial = head_commit.message

        return form

    def get_actions(self, request):
        actions = super(ReleaseAdmin, self).get_actions(request)
        del actions['delete_selected']
        return actions

admin.site.register(Release, ReleaseAdmin)


class DeploymentHostAdmin(admin.ModelAdmin):
    list_display = ('title', 'type', 'host', 'path', 'view_link',)
    ordering = ('title',)
    list_filter = ('type',)
    fieldsets = (
        (None, {
            'fields': ('title', 'url',),
        }),
        (_('Host'), {
            'fields': ('type', 'host', 'path', ),
        }),
        (_('Authentication'), {
            'fields': ('authtype', 'user', 'password', 'keypath', ),
        }),
    )

    def view_link(self, instance):
        if instance.url:
            return u'<a href="%s" target="_blank">%s</a>' % (instance.url, instance.url)
        else:
            return u''
    view_link.short_description = _('URL')
    view_link.allow_tags = True

admin.site.register(DeploymentHost, DeploymentHostAdmin)


class RegisteredUrlAdmin(admin.ModelAdmin):
    list_display = ('url', 'status', 'checked',)
    exclude = ('status', 'checked',)
    list_filter = ('status', 'checked',)
    ordering = ('url',)
    change_list_template = 'admin/release/registeredurl/change_list.html'

    def save_model(self, request, obj, form, change):
        obj.status = 0
        obj.checked = False
        obj.save()
        ValidateURLs.delay()

admin.site.register(RegisteredUrl, RegisteredUrlAdmin)
