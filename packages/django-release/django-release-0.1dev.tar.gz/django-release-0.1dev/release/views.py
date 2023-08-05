# -*- coding: utf-8 -*-
#

from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.contrib import messages
from release.tasks import DeployRelease, ValidateURLs
from release.models import Release
from release.forms import DeployForm
from django.template import RequestContext


def deploy(request, release_id):
    release = Release.objects.get(pk=release_id)

    if request.POST:
        form = DeployForm(request.POST)

        if form.is_valid():
            form.cleaned_data
            host_id = request.POST['deploymenthost']
            release.status = 1
            release.save()
            messages.success(request, 'Deployment wurde erfolgreich gestartet.')
            kwargs = {'release_id': release_id, 'host_id': host_id}
            DeployRelease.delay(**kwargs)

            return HttpResponseRedirect('/admin/release/release/')

    else:
        form = DeployForm()

    return render_to_response('admin/release/release/deploy_form.html',
                              {'form': form,
                               'release_id': release_id},
                              context_instance=RequestContext(request))


def validateurls(request):
    ValidateURLs.delay()

    return HttpResponseRedirect('/admin/release/registeredurl/')
