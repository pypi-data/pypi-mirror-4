# -*- coding: utf-8 -*-
#

from django import forms
from release.models import DeploymentHost
from django.utils.translation import ugettext as _


class DeployForm(forms.Form):
    deploymenthost = forms.ModelChoiceField(queryset=DeploymentHost.objects.all(), label=_('Host'), required=True)
