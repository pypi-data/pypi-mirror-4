"""
sentry.web.frontend.accounts
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2012 by the Sentry Team, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""
from crispy_forms.helper import FormHelper
from django.conf import settings as dj_settings
from django.contrib import messages
from django.core.context_processors import csrf
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.views.decorators.csrf import csrf_protect

from sentry.models import UserOption
from sentry.plugins import plugins
from sentry.web.decorators import login_required
from sentry.web.forms.accounts import AccountSettingsForm, NotificationSettingsForm, \
  AppearanceSettingsForm
from sentry.web.helpers import render_to_response
from sentry.utils.auth import get_auth_providers
from sentry.utils.safe import safe_execute


@csrf_protect
def login(request):
    from django.contrib.auth import login as login_
    from django.contrib.auth.forms import AuthenticationForm

    if request.user.is_authenticated():
        return login_redirect(request)

    form = AuthenticationForm(request, request.POST or None)
    if form.is_valid():
        login_(request, form.get_user())
        return login_redirect(request)

    request.session.set_test_cookie()

    AUTH_PROVIDERS = get_auth_providers()

    context = csrf(request)
    context.update({
        'form': form,
        'next': request.session.get('_next'),
        'AUTH_PROVIDERS': AUTH_PROVIDERS,
        'SOCIAL_AUTH_CREATE_USERS': dj_settings.SOCIAL_AUTH_CREATE_USERS,
    })
    return render_to_response('sentry/login.html', context, request)


@login_required
def login_redirect(request):
    default = reverse('sentry')
    login_url = request.session.pop('_next', None) or default
    if '//' in login_url:
        login_url = default
    elif login_url.startswith(reverse('sentry-login')):
        login_url = default
    return HttpResponseRedirect(login_url)


def logout(request):
    from django.contrib.auth import logout

    logout(request)

    return HttpResponseRedirect(reverse('sentry'))


@csrf_protect
@login_required
def settings(request):
    form = AccountSettingsForm(request.user, request.POST or None, initial={
        'email': request.user.email,
        'first_name': request.user.first_name,
    })
    if form.is_valid():
        form.save()
        messages.add_message(request, messages.SUCCESS, 'Your settings were saved.')
        return HttpResponseRedirect(request.path)

    context = csrf(request)
    context.update({
        'form': form,
        'page': 'settings',
    })
    return render_to_response('sentry/account/settings.html', context, request)


@csrf_protect
@login_required
def appearance_settings(request):
    options = UserOption.objects.get_all_values(user=request.user, project=None)

    form = AppearanceSettingsForm(request.user, request.POST or None, initial={
        'language': options.get('language') or request.LANGUAGE_CODE,
        'stacktrace_order': options.get('stacktrace_order'),
    })
    if form.is_valid():
        form.save()
        messages.add_message(request, messages.SUCCESS, 'Your settings were saved.')
        return HttpResponseRedirect(request.path)

    context = csrf(request)
    context.update({
        'form': form,
        'page': 'appearance',
    })
    return render_to_response('sentry/account/appearance.html', context, request)


@csrf_protect
@login_required
def notification_settings(request):
    forms = []
    for plugin in plugins.all():
        for form in safe_execute(plugin.get_notification_forms) or ():
            form = safe_execute(form, plugin, request.user, request.POST or None)
            if not form:
                continue
            helper = FormHelper()
            helper.form_tag = False
            forms.append((form, helper))

    # Ensure our form comes first
    helper = FormHelper()
    helper.form_tag = False
    forms = [
        (NotificationSettingsForm(request.user, request.POST or None), helper),
    ] + forms

    if request.POST:
        if all(f.is_valid() for f, h in forms):
            for form, helper in forms:
                form.save()
            messages.add_message(request, messages.SUCCESS, 'Your settings were saved.')
            return HttpResponseRedirect(request.path)

    context = csrf(request)
    context.update({
        'forms': forms,
        'page': 'notifications',
    })
    return render_to_response('sentry/account/notifications.html', context, request)


@csrf_protect
@login_required
def list_identities(request):
    from social_auth.models import UserSocialAuth

    identity_list = list(UserSocialAuth.objects.filter(user=request.user))

    AUTH_PROVIDERS = get_auth_providers()

    context = csrf(request)
    context.update({
        'identity_list': identity_list,
        'page': 'identities',
        'AUTH_PROVIDERS': AUTH_PROVIDERS,
    })
    return render_to_response('sentry/account/identities.html', context, request)
