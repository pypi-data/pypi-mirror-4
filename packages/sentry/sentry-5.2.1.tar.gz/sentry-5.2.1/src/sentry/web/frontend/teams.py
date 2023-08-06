"""
sentry.web.frontend.teams
~~~~~~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2012 by the Sentry Team, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""
from django.contrib import messages
from django.core.context_processors import csrf
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.views.decorators.csrf import csrf_protect
from django.utils.translation import ugettext as _

from sentry.constants import MEMBER_USER, MEMBER_OWNER
from sentry.models import PendingTeamMember, TeamMember
from sentry.permissions import can_add_team_member, can_remove_team, can_create_projects, \
  can_create_teams, can_edit_team_member, can_remove_team_member
from sentry.plugins import plugins
from sentry.web.decorators import login_required, has_team_access
from sentry.web.forms.teams import NewTeamForm, NewTeamAdminForm, \
  EditTeamForm, EditTeamAdminForm, EditTeamMemberForm, NewTeamMemberForm, \
  InviteTeamMemberForm, RemoveTeamForm, AcceptInviteForm
from sentry.web.helpers import render_to_response


@login_required
def team_list(request):
    return render_to_response('sentry/teams/list.html', {}, request)


@login_required
@csrf_protect
def create_new_team(request):
    if not can_create_teams(request.user):
        return HttpResponseRedirect(reverse('sentry'))

    if request.user.has_perm('sentry.can_add_team'):
        form_cls = NewTeamAdminForm
        initial = {
            'owner': request.user.username,
        }
    else:
        form_cls = NewTeamForm
        initial = {}

    form = form_cls(request.POST or None, initial=initial)
    if form.is_valid():
        team = form.save(commit=False)
        if not team.owner_id:
            team.owner = request.user
        team.save()
        return HttpResponseRedirect(reverse('sentry-manage-team', args=[team.slug]))

    context = csrf(request)
    context.update({
        'form': form,
    })

    return render_to_response('sentry/teams/new.html', context, request)


@has_team_access(MEMBER_OWNER)
@csrf_protect
def manage_team(request, team):
    result = plugins.first('has_perm', request.user, 'edit_team', team)
    if result is False and not request.user.has_perm('sentry.can_change_team'):
        return HttpResponseRedirect(reverse('sentry'))

    can_admin_team = request.user == team.owner or request.user.has_perm('sentry.can_add_team')

    if can_admin_team:
        form_cls = EditTeamAdminForm
    else:
        form_cls = EditTeamForm

    form = form_cls(request.POST or None, initial={
        'owner': team.owner,
    }, instance=team)

    # XXX: form.is_valid() changes the foreignkey
    original_owner = team.owner
    if form.is_valid():

        team = form.save()
        if team.owner != original_owner:
            # Update access for new membership if it's changed
            # (e.g. member used to be USER, but is now OWNER)
            team.member_set.filter(user=team.owner).update(type=MEMBER_OWNER)

        messages.add_message(request, messages.SUCCESS,
            _('Changes to your team were saved.'))

        return HttpResponseRedirect(request.path)

    context = csrf(request)
    context.update({
        'can_remove_team': can_remove_team(request.user, team),
        'page': 'details',
        'form': form,
        'team': team,
    })

    return render_to_response('sentry/teams/manage.html', context, request)


@has_team_access(MEMBER_OWNER)
@csrf_protect
def manage_team_projects(request, team):
    result = plugins.first('has_perm', request.user, 'edit_team', team)
    if result is False and not request.user.has_perm('sentry.can_change_team'):
        return HttpResponseRedirect(reverse('sentry'))

    project_list = list(team.project_set.all())

    context = csrf(request)
    context.update({
        'can_add_project': can_create_projects(request.user, team),
        'page': 'projects',
        'team': team,
        'project_list': project_list,
    })

    return render_to_response('sentry/teams/projects/index.html', context, request)


@has_team_access(MEMBER_OWNER)
@csrf_protect
def manage_team_members(request, team):
    result = plugins.first('has_perm', request.user, 'edit_team', team)
    if result is False and not request.user.has_perm('sentry.can_change_team'):
        return HttpResponseRedirect(reverse('sentry'))

    member_list = [(pm, pm.user) for pm in team.member_set.select_related('user').order_by('user__username')]
    pending_member_list = [(pm, pm.email) for pm in team.pending_member_set.all().order_by('email')]

    context = csrf(request)
    context.update({
        'can_add_member': can_add_team_member(request.user, team),
        'page': 'members',
        'team': team,
        'member_list': member_list,
        'pending_member_list': pending_member_list,
    })

    return render_to_response('sentry/teams/members/index.html', context, request)


@has_team_access(MEMBER_OWNER)
@csrf_protect
def remove_team(request, team):
    if not can_remove_team(request.user, team):
        return HttpResponseRedirect(reverse('sentry'))

    form = RemoveTeamForm(request.POST or None)

    if form.is_valid():
        team.delete()
        return HttpResponseRedirect(reverse('sentry-team-list'))

    context = csrf(request)
    context.update({
        'page': 'settings',
        'form': form,
        'team': team,
    })

    return render_to_response('sentry/teams/remove.html', context, request)


@csrf_protect
@has_team_access(MEMBER_OWNER)
def new_team_member(request, team):
    can_add_member = can_add_team_member(request.user, team)
    if not can_add_member:
        return HttpResponseRedirect(reverse('sentry'))

    initial = {
        'type': MEMBER_USER,
    }

    invite_form = InviteTeamMemberForm(team, request.POST or None, initial=initial, prefix='invite')
    add_form = NewTeamMemberForm(team, request.POST or None, initial=initial, prefix='add')

    if add_form.is_valid():
        pm = add_form.save(commit=False)
        pm.team = team
        pm.save()

        messages.add_message(request, messages.SUCCESS,
            _('The team member was added.'))

        return HttpResponseRedirect(reverse('sentry-edit-team-member', args=[team.slug, pm.id]))

    elif invite_form.is_valid():
        pm = invite_form.save(commit=False)
        pm.team = team
        pm.save()

        pm.send_invite_email()

        return HttpResponseRedirect(reverse('sentry-manage-team', args=[team.slug]) + '?success=1')

    context = csrf(request)
    context.update({
        'page': 'members',
        'team': team,
        'add_form': add_form,
        'invite_form': invite_form,
    })

    return render_to_response('sentry/teams/members/new.html', context, request)


@csrf_protect
def accept_invite(request, member_id, token):
    try:
        pending_member = PendingTeamMember.objects.get(pk=member_id)
    except PendingTeamMember.DoesNotExist:
        return HttpResponseRedirect(reverse('sentry'))

    if pending_member.token != token:
        return HttpResponseRedirect(reverse('sentry'))

    team = pending_member.team

    context = {
        'team': team,
        'team_owner': team.get_owner_name(),
        'project_list': list(team.project_set.filter(status=0)),
    }

    if not request.user.is_authenticated():
        # Show login or register form
        request.session['_next'] = request.get_full_path()
        request.session['can_register'] = True

        return render_to_response('sentry/teams/members/accept_invite_unauthenticated.html', context, request)

    if request.method == 'POST':
        form = AcceptInviteForm(request.POST)
    else:
        form = AcceptInviteForm()

    if form.is_valid():
        team.member_set.get_or_create(
            user=request.user,
            defaults={
                'type': pending_member.type,
            }
        )

        request.session.pop('can_register', None)

        pending_member.delete()

        messages.add_message(request, messages.SUCCESS,
            _('You have been added to the %r team.') % (team.name.encode('utf-8'),))

        return HttpResponseRedirect(reverse('sentry', args=[team.slug]))

    context['form'] = form

    return render_to_response('sentry/teams/members/accept_invite.html', context, request)


@csrf_protect
@has_team_access(MEMBER_OWNER)
def edit_team_member(request, team, member_id):
    try:
        member = team.member_set.get(pk=member_id)
    except TeamMember.DoesNotExist:
        return HttpResponseRedirect(reverse('sentry-manage-team', args=[team.slug]))

    if not can_edit_team_member(request.user, member):
        return HttpResponseRedirect(reverse('sentry'))

    form = EditTeamMemberForm(team, request.POST or None, instance=member)
    if form.is_valid():
        member = form.save(commit=True)

        messages.add_message(request, messages.SUCCESS,
            _('Changes to your team member were saved.'))

        return HttpResponseRedirect(request.path)

    context = csrf(request)
    context.update({
        'page': 'members',
        'member': member,
        'team': team,
        'form': form,
    })

    return render_to_response('sentry/teams/members/edit.html', context, request)


@csrf_protect
@has_team_access(MEMBER_OWNER)
def remove_team_member(request, team, member_id):
    try:
        member = team.member_set.get(pk=member_id)
    except TeamMember.DoesNotExist:
        return HttpResponseRedirect(reverse('sentry-manage-team', args=[team.slug]))

    if member.user == team.owner:
        return HttpResponseRedirect(reverse('sentry-manage-team', args=[team.slug]))

    if not can_remove_team_member(request.user, member):
        return HttpResponseRedirect(reverse('sentry'))

    if request.POST:
        member.delete()

        return HttpResponseRedirect(reverse('sentry-manage-team', args=[team.slug]))

    context = csrf(request)
    context.update({
        'page': 'members',
        'member': member,
        'team': team,
    })

    return render_to_response('sentry/teams/members/remove.html', context, request)


@csrf_protect
@has_team_access(MEMBER_OWNER)
def suspend_team_member(request, team, member_id):
    try:
        member = team.member_set.get(pk=member_id)
    except TeamMember.DoesNotExist:
        return HttpResponseRedirect(reverse('sentry-manage-team', args=[team.slug]))

    if member.user == team.owner:
        return HttpResponseRedirect(reverse('sentry-manage-team', args=[team.slug]))

    result = plugins.first('has_perm', request.user, 'suspend_team_member', member)
    if result is False and not request.user.has_perm('sentry.can_change_teammember'):
        return HttpResponseRedirect(reverse('sentry'))

    member.update(is_active=False)

    messages.add_message(request, messages.SUCCESS,
        _('The team member was suspended.'))

    return HttpResponseRedirect(reverse('sentry-manage-team', args=[team.slug]))


@csrf_protect
@has_team_access(MEMBER_OWNER)
def restore_team_member(request, team, member_id):
    try:
        member = team.member_set.get(pk=member_id)
    except TeamMember.DoesNotExist:
        return HttpResponseRedirect(reverse('sentry-manage-team', args=[team.slug]))

    if member.user == team.owner:
        return HttpResponseRedirect(reverse('sentry-manage-team', args=[team.slug]))

    result = plugins.first('has_perm', request.user, 'restore_team_member', member)
    if result is False and not request.user.has_perm('sentry.can_change_teammember'):
        return HttpResponseRedirect(reverse('sentry'))

    member.update(is_active=True)

    messages.add_message(request, messages.SUCCESS,
        _('The team member was made active.'))

    return HttpResponseRedirect(reverse('sentry-manage-team', args=[team.slug]))


@csrf_protect
@has_team_access(MEMBER_OWNER)
def remove_pending_team_member(request, team, member_id):
    try:
        member = team.pending_member_set.get(pk=member_id)
    except PendingTeamMember.DoesNotExist:
        return HttpResponseRedirect(reverse('sentry-manage-team', args=[team.slug]))

    result = plugins.first('has_perm', request.user, 'remove_team_member', member)
    if result is False and not request.user.has_perm('sentry.can_remove_teammember'):
        return HttpResponseRedirect(reverse('sentry'))

    member.delete()

    messages.add_message(request, messages.SUCCESS,
        _('The team member was removed.'))

    return HttpResponseRedirect(reverse('sentry-manage-team', args=[team.slug]))


@csrf_protect
@has_team_access(MEMBER_OWNER)
def reinvite_pending_team_member(request, team, member_id):
    try:
        member = team.pending_member_set.get(pk=member_id)
    except PendingTeamMember.DoesNotExist:
        return HttpResponseRedirect(reverse('sentry-manage-team', args=[team.slug]))

    result = plugins.first('has_perm', request.user, 'add_team_member', member)
    if result is False and not request.user.has_perm('sentry.can_add_teammember'):
        return HttpResponseRedirect(reverse('sentry'))

    member.send_invite_email()

    messages.add_message(request, messages.SUCCESS,
        _('An email was sent to the pending team member.'))

    return HttpResponseRedirect(reverse('sentry-manage-team', args=[team.slug]))


@csrf_protect
@has_team_access(MEMBER_OWNER)
def create_new_team_project(request, team):
    from sentry.web.forms.projects import NewProjectAdminForm, NewProjectForm

    if not can_create_projects(request.user, team):
        return HttpResponseRedirect(reverse('sentry'))

    if request.user.has_perm('sentry.can_add_project'):
        form_cls = NewProjectAdminForm
        initial = {
            'owner': request.user.username,
        }
    else:
        form_cls = NewProjectForm
        initial = {}

    form = form_cls(request.POST or None, initial=initial)
    if form.is_valid():
        project = form.save(commit=False)
        project.team = team
        if not project.owner:
            project.owner = request.user
        project.save()

        if project.platform not in (None, 'other'):
            return HttpResponseRedirect(reverse('sentry-docs-client', args=[project.slug, project.platform]))
        return HttpResponseRedirect(reverse('sentry-get-started', args=[project.slug]))

    context = csrf(request)
    context.update({
        'form': form,
        'team': team,
        'page': 'projects',
    })

    return render_to_response('sentry/teams/projects/new.html', context, request)
