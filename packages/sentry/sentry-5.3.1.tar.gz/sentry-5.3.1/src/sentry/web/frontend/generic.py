"""
sentry.web.frontend.generic
~~~~~~~~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2010-2012 by the Sentry Team, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""
from django.http import HttpResponseRedirect, Http404, HttpResponseNotModified, \
  HttpResponse
from django.conf import settings as dj_settings
from django.core.urlresolvers import reverse

from sentry.conf import settings
from sentry.models import Team
from sentry.web.decorators import login_required

STATIC_PATH_CACHE = {}


@login_required
def dashboard(request, template='dashboard.html'):
    team_list = Team.objects.get_for_user(request.user)
    if not team_list:
        return HttpResponseRedirect(reverse('sentry-new-team'))

    # This cookie gets automatically set by render_to_response
    last_team = request.session.get('team')
    if last_team in team_list:
        team = team_list[last_team]
    else:
        team = team_list.values()[0]

    # Redirect to first team
    # TODO: maybe store this in a cookie and redirect to last seen team?
    return HttpResponseRedirect(reverse('sentry', args=[team.slug]))


def wall_display(request):
    return dashboard(request, 'wall.html')


def static_media(request, module, path, root=None):
    """
    Serve static files below a given point in the directory structure.
    """
    from django.utils.http import http_date
    from django.views.static import was_modified_since
    import mimetypes
    import os.path
    import posixpath
    import stat
    import urllib

    if root:
        document_root = root
    elif module == 'sentry':
        document_root = os.path.join(settings.MODULE_ROOT, 'static', module)
    elif module == dj_settings.COMPRESS_OUTPUT_DIR:
        document_root = os.path.join(dj_settings.STATIC_ROOT, module)
    elif module not in dj_settings.INSTALLED_APPS:
        raise Http404('Invalid module provided.')
    else:
        if module not in STATIC_PATH_CACHE:
            try:
                mod = __import__(module)
            except ImportError:
                raise Http404('Import error raised while fetching module')

            STATIC_PATH_CACHE[module] = os.path.normpath(os.path.join(
                os.path.dirname(mod.__file__),
                'static',
                module,
            ))

        document_root = STATIC_PATH_CACHE[module]

    path = posixpath.normpath(urllib.unquote(path))
    path = path.lstrip('/')
    newpath = ''
    for part in path.split('/'):
        if not part:
            # Strip empty path components.
            continue
        drive, part = os.path.splitdrive(part)
        head, part = os.path.split(part)
        if part in (os.curdir, os.pardir):
            # Strip '.' and '..' in path.
            continue
        newpath = os.path.join(newpath, part).replace('\\', '/')
    if newpath and path != newpath:
        return HttpResponseRedirect(newpath)
    fullpath = os.path.join(document_root, newpath)
    if os.path.isdir(fullpath):
        raise Http404('Directory indexes are not allowed here.')
    if not os.path.exists(fullpath):
        raise Http404('"%s" does not exist' % fullpath)
    # Respect the If-Modified-Since header.
    statobj = os.stat(fullpath)
    mimetype = mimetypes.guess_type(fullpath)[0] or 'application/octet-stream'
    if not was_modified_since(request.META.get('HTTP_IF_MODIFIED_SINCE'),
                              statobj[stat.ST_MTIME], statobj[stat.ST_SIZE]):
        return HttpResponseNotModified(mimetype=mimetype)
    contents = open(fullpath, 'rb').read()
    response = HttpResponse(contents, mimetype=mimetype)
    response['Last-Modified'] = http_date(statobj[stat.ST_MTIME])
    response['Content-Length'] = len(contents)
    return response
