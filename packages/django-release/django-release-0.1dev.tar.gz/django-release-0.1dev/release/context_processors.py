
from .models import Release


def releaseinprogress(request):
    release = Release.objects.filter(status=1)
    releaseinprogress = False

    if len(release) > 0:
        releaseinprogress = True

    return {'releaseinprogress': releaseinprogress}
