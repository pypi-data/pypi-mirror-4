import os
import hashlib
from hashlib import md5
from datetime import datetime, timedelta

from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.core.management import call_command

from djcelery.models import TaskMeta
from geraldo.generators import PDFGenerator
from tendenci.apps.notifications.utils import send_welcome_email

from tendenci.core.site_settings.utils import get_setting
from tendenci.core.event_logs.models import EventLog
from tendenci.core.base.http import Http403
from tendenci.core.base.decorators import password_required
from tendenci.core.base.utils import send_email_notification
from tendenci.core.perms.utils import has_perm, update_perms_and_save, get_query_filters
from tendenci.addons.corporate_memberships.models import CorporateMembership, IndivMembEmailVeri8n
from reports import ReportNewMems
from tendenci.core.files.models import File
from tendenci.core.exports.utils import render_csv, run_export_task

from tendenci.addons.memberships.models import (App, AppEntry, Membership,
    MembershipType, Notice, AppField, MembershipImport)
from tendenci.addons.memberships.forms import (AppCorpPreForm, MembershipForm,
    MemberApproveForm, ReportForm, EntryEditForm, ExportForm,
    AppEntryForm)
from tendenci.addons.memberships.utils import (is_import_valid, prepare_chart_data,
    get_days, get_over_time_stats, get_status_filter,
    get_membership_stats, NoMembershipTypes)
from tendenci.addons.memberships.importer.forms import ImportMapForm, UploadForm
from tendenci.addons.memberships.importer.utils import parse_mems_from_csv
from tendenci.addons.memberships.importer.tasks import ImportMembershipsTask


def membership_index(request):
    if request.user.profile:
        if request.user.profile.is_superuser or request.user.profile.is_staff:
            return HttpResponseRedirect(reverse('membership.application_entries_search'))
    return HttpResponseRedirect(reverse('membership.search'))


def membership_search(request, template_name="memberships/search.html"):
    membership_view_perms = get_setting('module', 'memberships', 'memberprotection')

    if not membership_view_perms == "public":
        return HttpResponseRedirect(reverse('profile.search') + "?members=on")

    query = request.GET.get('q')
    mem_type = request.GET.get('type')
    total_count = Membership.objects.all().count()
    if get_setting('site', 'global', 'searchindex') and (total_count > 1000 or query):
        members = Membership.objects.search(query, user=request.user)
        if mem_type:
            members = members.filter(mem_type=mem_type)
        members = members.order_by('last_name')
    else:
        filters = get_query_filters(request.user, 'memberships.view_membership')
        members = Membership.objects.filter(filters).distinct()
        if mem_type:
            members = members.filter(membership_type__pk=mem_type)
        members = members.exclude(status_detail='expired')
        members = members.order_by('user__last_name')
    types = MembershipType.objects.all()

    EventLog.objects.log()

    return render_to_response(template_name, {'members': members, 'types': types},
        context_instance=RequestContext(request))


@login_required
def membership_details(request, id=0, template_name="memberships/details.html"):
    """
    Membership details.
    """
    membership = get_object_or_404(Membership, pk=id)

    if not has_perm(request.user, 'memberships.view_membership', membership):
        raise Http403

    EventLog.objects.log(instance=membership)

    return render_to_response(template_name, {'membership': membership},
        context_instance=RequestContext(request))


@login_required
def membership_edit(request, id, form_class=MembershipForm, template_name="memberships/edit.html"):
    """
    Membership edit.
    """
    from tendenci.apps.user_groups.models import GroupMembership
    membership = get_object_or_404(Membership, pk=id)

    if not has_perm(request.user, 'memberships.change_membership', membership):
        raise Http403

    if request.method == "POST":
        form = form_class(request.POST, instance=membership, user=request.user)

        if form.is_valid():
            membership = form.save(commit=False)

            # update all permissions and save the model
            membership = update_perms_and_save(request, form, membership)

            # add or remove from group -----
            if membership.is_active():  # should be in group; make sure they're in
                membership.membership_type.group.add_user(membership.user)
            else:  # should not be in group; make sure they're out
                GroupMembership.objects.filter(
                    member=membership.user,
                    group=membership.membership_type.group
                ).delete()
            # -----

            # update member-number on profile
            membership.user.profile.refresh_member_number()

            messages.add_message(request, messages.SUCCESS, 'Successfully updated %s' % membership)

            return redirect('membership.details', membership.pk)
    else:
        form = form_class(instance=membership, user=request.user)

    return render_to_response(template_name, {
        'membership': membership,
        'form': form,
    }, context_instance=RequestContext(request))


@login_required
def membership_delete(request, id, template_name="memberships/delete.html"):
    """Membership delete"""
    membership = get_object_or_404(Membership, pk=id)

    if not has_perm(request.user, 'memberships.delete_membership', membership):
        raise Http403

    if request.method == "POST":

        messages.add_message(request, messages.SUCCESS, 'Successfully deleted %s' % membership)

        return HttpResponseRedirect(reverse('membership.search'))

    return render_to_response(template_name, {'membership': membership},
        context_instance=RequestContext(request))


def download_template(request, slug=''):
    """
    Return a csv [download response] of the application specified via slug
    """
    from tendenci.addons.memberships.utils import make_csv
    return make_csv(slug=slug)


def application_details(request, template_name="memberships/applications/details.html", **kwargs):
    """
    Display a built membership application and handle submission.
    """

    slug = kwargs.get('slug')
    cmb_id = kwargs.get('cmb_id')
    imv_id = kwargs.get('imv_id', 0)
    imv_guid = kwargs.get('imv_guid')
    secret_hash = kwargs.get('secret_hash', '')

    if not slug:
        raise Http404
    user = request.user

    app = get_object_or_404(App, slug=slug)
    if not app.allow_view_by(user):
        raise Http403

    # if this app is for corporation individuals, redirect them to corp-pre page if
    # they have not passed the security check.
    corporate_membership = None
    if hasattr(app, 'corp_app') and app.corp_app:
        if not cmb_id:
            # redirect them to the corp_pre page
            return redirect(reverse('membership.application_details_corp_pre', args=[app.slug]))

        corporate_membership = get_object_or_404(CorporateMembership, id=cmb_id)
        # check if they have verified their email or entered the secret code
        is_verified = False
        if request.user.profile.is_superuser or app.corp_app.authentication_method == 'admin':
            is_verified = True
        elif app.corp_app.authentication_method == 'email':
            try:
                indiv_veri = IndivMembEmailVeri8n.objects.get(pk=imv_id,
                                                              guid=imv_guid)
                if indiv_veri.verified:
                    is_verified = True
            except IndivMembEmailVeri8n.DoesNotExist:
                pass

        elif app.corp_app.authentication_method == 'secret_code':
            tmp_secret_hash = md5('%s%s' % (corporate_membership.secret_code,
                                    request.session.get('corp_hash_random_string', ''))).hexdigest()
            if secret_hash == tmp_secret_hash:
                is_verified = True

        if not is_verified:
            return redirect(reverse('membership.application_details_corp_pre', args=[slug]))

    EventLog.objects.log(instance=app)

    initial_dict = {}
    if hasattr(user, 'memberships'):
        is_only_a_member = [
            user.profile.is_superuser == False,
            user.profile.is_member == True,
        ]

        if corporate_membership:
            # exclude corp. reps, creator and owner - they should be able to add new
            is_only_a_member.append(corporate_membership.allow_edit_by(user) == False)

        if user.profile.is_superuser:
            username = request.GET.get('username', unicode())
            if username:
                try:
                    registrant = User.objects.get(username=username)
                    # get info from last time this app was filled out
                    initial_dict = app.get_initial_info(registrant)
                except:
                    pass

        elif all(is_only_a_member):
            # get info from last time this app was filled out
            initial_dict = app.get_initial_info(user)

    pending_entries = []

    if hasattr(user, 'appentry_set'):
        pending_entries = user.appentry_set.filter(
            is_approved__isnull=True  # pending
        )

        # if an application entry was submitted
        # after your current membership was created
        if user.memberships.get_membership():
            pending_entries.filter(
                entry_time__gte=user.memberships.get_membership().subscribe_dt
            )

    try:
        app_entry_form = AppEntryForm(
                app,
                request.POST or None,
                request.FILES or None,
                user=user,
                corporate_membership=corporate_membership,
                initial=initial_dict
            )
    except NoMembershipTypes as e:
        print e

        user_memberships = None
        if hasattr(user, 'memberships'):
            user_memberships = user.memberships.all()
        # non-admin has no membership-types available in this application
        # let them know to wait for their renewal period before trying again
        return render_to_response("memberships/applications/no-renew.html", {
            "app": app, "user": user, "memberships": user_memberships},
            context_instance=RequestContext(request))

    if request.method == "POST":
        if app_entry_form.is_valid():

            entry = app_entry_form.save(commit=False)
            entry_invoice = entry.save_invoice()

            if user.is_authenticated():
                entry.user = user
                entry.is_renewal = all(is_only_a_member)

            # add all permissions and save the model
            entry = update_perms_and_save(request, app_entry_form, entry)

            # administrators go to approve/disapprove page
            if user.profile.is_superuser:
                return redirect(reverse('membership.application_entries', args=[entry.pk]))

            # send "joined" notification
            Notice.send_notice(
                entry=entry,
                request=request,
                emails=entry.email,
                notice_type='join',
                membership_type=entry.membership_type,
            )

            if entry_invoice.total == 0:
                if not entry_invoice.is_tendered:
                    entry_invoice.tender(request.user)

            # online payment
            if entry_invoice.total > 0 and entry.payment_method and entry.payment_method.is_online:

                return HttpResponseRedirect(reverse(
                    'payment.pay_online',
                    args=[entry_invoice.pk, entry_invoice.guid]
                ))

            if not entry.approval_required():

                entry.user, created = entry.get_or_create_user()
                if created:
                    send_welcome_email(entry.user)

                entry.approve()

                # silence old memberships within renewal period
                Membership.objects.silence_old_memberships(entry.user)

                # get user from the membership since it's null in the entry
                entry.user = entry.membership.user

                # send "approved" notification
                Notice.send_notice(
                    request=request,
                    emails=entry.email,
                    notice_type='approve',
                    membership=entry.membership,
                    membership_type=entry.membership_type,
                )

                # log - entry approval
                EventLog.objects.log(instance=entry)

            # log - entry submission
            EventLog.objects.log(instance=entry)

            return redirect(entry.confirmation_url)

    return render_to_response(template_name, {
            'app': app,
            'app_entry_form': app_entry_form,
            'pending_entries': pending_entries,
            }, context_instance=RequestContext(request))


def application_details_corp_pre(request, slug, cmb_id=None, template_name="memberships/applications/details_corp_pre.html"):

    try:
        app = App.objects.get(slug=slug)
    except App.DoesNotExist:
        raise Http404

    if not hasattr(app, 'corp_app'):
        raise Http404

    if not app.corp_app:
        raise Http404

    form = AppCorpPreForm(request.POST or None)
    if request.user.profile.is_superuser or app.corp_app.authentication_method == 'admin':
        del form.fields['secret_code']
        del form.fields['email']
        from utils import get_corporate_membership_choices
        form.fields['corporate_membership_id'].choices = get_corporate_membership_choices()
        if cmb_id:
            form.fields['corporate_membership_id'].initial = cmb_id
        form.auth_method = 'corporate_membership_id'

    elif app.corp_app.authentication_method == 'email':
        del form.fields['corporate_membership_id']
        del form.fields['secret_code']
        form.auth_method = 'email'
    else:  # secret_code
        del form.fields['corporate_membership_id']
        del form.fields['email']
        form.auth_method = 'secret_code'

    if request.method == "POST":
        if form.is_valid():
            # find the corporate_membership_id and redirect to membership.application_details
            if form.auth_method == 'corporate_membership_id':
                corporate_membership_id = form.cleaned_data['corporate_membership_id']
            else:
                corporate_membership_id = form.corporate_membership_id

                if form.auth_method == 'email':
                    corp_memb = CorporateMembership.objects.get(pk=corporate_membership_id)
                    try:
                        indiv_veri = IndivMembEmailVeri8n.objects.get(corporate_membership=corp_memb,
                                                                verified_email=form.cleaned_data['email'])
                        if indiv_veri.verified:
                            is_verified = True
                        else:
                            is_verified = False
                    except IndivMembEmailVeri8n.DoesNotExist:
                        is_verified = False
                        indiv_veri = IndivMembEmailVeri8n()
                        indiv_veri.corporate_membership = corp_memb
                        indiv_veri.verified_email = form.cleaned_data['email']
                        if request.user and not request.user.is_anonymous():
                            indiv_veri.creator = request.user
                        indiv_veri.save()

                    # send an email to the user to verify the email address
                    # then redirect them to the verification conf page
                    # they'll need to follow the instruction in the email
                    # to continue to sign up.
                    if not is_verified:
                        recipients = [indiv_veri.verified_email]
                        extra_context = {
                            'object': indiv_veri,
                            'app': app,
                            'corp_memb': corp_memb,
                            'request': request,
                        }
                        send_email_notification('membership_corp_indiv_verify_email', recipients, extra_context)

                        return redirect(reverse('membership.email__to_verify_conf'))
                    else:
                        # the email address is verified
                        return redirect(reverse('membership.application_details_via_corp_domain',
                                                args=[app.slug,
                                                indiv_veri.corporate_membership.id,
                                                indiv_veri.pk,
                                                indiv_veri.guid]))
                if form.auth_method == 'secret_code':
                    # secret code hash
                    random_string = User.objects.make_random_password(length=4, allowed_chars='abcdefghjkmnpqrstuvwxyz')
                    request.session['corp_hash_random_string'] = random_string
                    secret_code = form.cleaned_data['secret_code']
                    secret_hash = md5('%s%s' % (secret_code, random_string)).hexdigest()
                    return redirect(reverse('membership.application_details_via_corp_secret_code',
                                            args=[app.slug,
                                                corporate_membership_id,
                                                secret_hash]))

            return redirect(reverse('membership.application_details', args=[app.slug, corporate_membership_id]))

    c = {'app': app, "form": form}
    return render_to_response(template_name, c,
        context_instance=RequestContext(request))


def email_to_verify_conf(request, template_name="memberships/applications/email_to_verify_conf.html"):
    return render_to_response(template_name,
        context_instance=RequestContext(request))


def verify_email(request, id=0, guid=None, template_name="memberships/applications/verify_email.html"):
    indiv_veri = get_object_or_404(IndivMembEmailVeri8n, id=id, guid=guid)
    if not indiv_veri.verified:
        indiv_veri.verified = True
        indiv_veri.verified_dt = datetime.now()
        if request.user and not request.user.is_anonymous():
            indiv_veri.updated_by = request.user
            indiv_veri.save()

    # let them continue to sign up for membership
    return redirect(reverse('membership.application_details_via_corp_domain',
                            args=[indiv_veri.corporate_membership.corp_app.memb_app.slug,
                                  indiv_veri.corporate_membership.id,
                                  indiv_veri.pk,
                                  indiv_veri.guid]))


def application_confirmation(request, hash=None, template_name="memberships/entries/details.html"):
    """
    Display this confirmation have a membership application is submitted.
    """

    if not hash:
        raise Http404

    entry = get_object_or_404(AppEntry, hash=hash)

    return render_to_response(template_name, {'is_confirmation': True, 'entry': entry},
        context_instance=RequestContext(request))


@login_required
def application_entries(request, id=None, template_name="memberships/entries/details.html"):
    """
    Displays the details of a membership application entry.
    """

    if not id:
        return redirect(reverse('membership.application_entries_search'))

    entry = get_object_or_404(AppEntry, id=id)
    if not entry.allow_view_by(request.user):
        raise Http403

    EventLog.objects.log(instance=entry)

    if request.method == "POST":
        form = MemberApproveForm(entry, request.POST)
        if form.is_valid():

            status = request.POST.get('status', '')
            approve = (status.lower() == 'approve') or (status.lower() == 'approve renewal')

            entry.judge = request.user

            if approve:
                user_pk = int(form.cleaned_data['users'])
                if user_pk:
                    entry.user = User.objects.get(pk=user_pk)
                else:
                    entry.user = User.objects.create_user(**{
                        'username': entry.spawn_username(entry.first_name, entry.last_name),
                        'email': entry.email,
                        'password': hashlib.sha1(entry.email).hexdigest()[:6]
                    })
                    send_welcome_email(entry.user)

                # update application, user,
                # group, membership, and archive
                entry.approve()

                # silence old memberships within renewal period
                Membership.objects.silence_old_memberships(entry.user)

                # execute field functions (group subscriptions)
                entry.execute_field_functions()

                # send "approved" notification
                Notice.send_notice(
                    request=request,
                    entry=entry,
                    emails=entry.email,
                    notice_type='approve',
                    membership=entry.membership,
                    membership_type=entry.membership_type,
                )

                EventLog.objects.log(instance=entry, action="approve")

            else:  # if not approved
                entry.disapprove()

                # send "disapproved" notification
                Notice.send_notice(
                    entry=entry,
                    request=request,
                    emails=entry.email,
                    notice_type='disapprove',
                    membership_type=entry.membership_type,
                )

                EventLog.objects.log(instance=entry, action="disapprove")

            return redirect(reverse('membership.application_entries', args=[entry.pk]))

    else:  # if request != POST
        form = MemberApproveForm(entry)

    return render_to_response(template_name, {
        'entry': entry,
        'form': form,
        }, context_instance=RequestContext(request))


@login_required
def application_entries_print(request, id=None, template_name="memberships/entries/print-details.html"):
    """
    Displays the print details of a membership application entry.
    """

    if not id:
        return redirect(reverse('membership.application_entries_search'))

    entry = get_object_or_404(AppEntry, id=id)
    if not entry.allow_view_by(request.user):
        raise Http403

    # log entry view
    EventLog.objects.log(**{
        'event_id': 1085001,
        'event_data': '%s (%d) print viewed by %s' % (entry._meta.object_name, entry.pk, request.user),
        'description': '%s print viewed' % entry._meta.object_name,
        'user': request.user,
        'request': request,
        'instance': entry,
    })

    return render_to_response(template_name, {
        'entry': entry,
        }, context_instance=RequestContext(request))


@login_required
def entry_edit(request, id=0, template_name="memberships/entries/edit.html"):
    """
    Edit membership application entry page.
    """
    entry = get_object_or_404(AppEntry, id=id)  # exists

    if not request.user.profile.is_superuser:
        raise Http403  # not permitted

    if request.method == "POST":
        form = EntryEditForm(request.POST, instance=entry)
        if form.is_valid():
            entry = form.save()

            EventLog.objects.log(instance=entry)

            messages.add_message(
                request,
                messages.INFO,
                'Entry Sucessfully Updated',
            )

            return redirect(reverse('membership.application_entries', args=[entry.pk]))

    else:
        form = EntryEditForm(instance=entry)

    return render_to_response(template_name, {
        'entry': entry,
        'form': form,
        }, context_instance=RequestContext(request))


@login_required
def entry_delete(request, id=0, template_name="memberships/entries/delete.html"):
    """
    Delete membership application entry.
    """
    entry = get_object_or_404(AppEntry, id=id)  # exists

    if not request.user.profile.is_superuser:
        raise Http403  # not permitted

    if request.method == "POST":
        EventLog.objects.log(instance=entry)
        messages.add_message(request, messages.INFO, "Deleted %s" % entry)
        entry.delete()

        return redirect("membership.application_entries_search")

    return render_to_response(template_name, {
        'entry': entry,
    }, context_instance=RequestContext(request))


@login_required
def application_entries_search(request, template_name="memberships/entries/search.html"):
    """
    Displays a page for searching membership application entries.
    """
    query = request.GET.get('q')
    if get_setting('site', 'global', 'searchindex') and query:
        entries = AppEntry.objects.search(query, user=request.user)
    else:
        status = request.GET.get('status', None)

        filters = get_query_filters(request.user, 'memberships.view_appentry')
        entries = AppEntry.objects.filter(filters).distinct()
        if status:
            status_filter = get_status_filter(status)
            entries = entries.filter(status_filter)

        entries = entries.select_related()

    entries = entries.order_by('-entry_time')

    apps = App.objects.all()
    types = MembershipType.objects.all()

    EventLog.objects.log()

    return render_to_response(template_name, {
        'entries': entries,
        'apps': apps,
        'types': types,
        }, context_instance=RequestContext(request))


@login_required
def notice_email_content(request, id, template_name="memberships/notices/email_content.html"):
    if not request.user.profile.is_superuser:
        raise Http403
    notice = get_object_or_404(Notice, pk=id)

    EventLog.objects.log(instance=notice)

    return render_to_response(template_name, {
        'notice': notice,
        }, context_instance=RequestContext(request))


@login_required
@password_required
def membership_import_upload(request, template_name='memberships/import-upload-file.html'):
    """
    This is the upload view for the membership imports.
    This will upload the membership import file and then redirect the user
    to the import mapping/preview page of the import file
    """

    if not request.user.profile.is_superuser:
        raise Http403

    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            # reset the password_promt session
            request.session['password_promt'] = False
            cleaned_data = form.cleaned_data
            app = cleaned_data['app']
            interactive = cleaned_data['interactive']
            override = cleaned_data['override']
            key = cleaned_data['key']

            memport = MembershipImport.objects.create(
                app=app,
                interactive=interactive,
                override=override,
                key=key,
                creator=request.user
            )

            csv = File.objects.save_files_for_instance(request, memport)[0]

            # hiding membership import
            csv.allow_anonymous_view = False
            csv.allow_user_view = False
            csv.is_public = False
            csv.save()

            file_path = str(csv.file.name)
            #file_path = os.path.join(settings.MEDIA_ROOT, csv.file.name)

            import_valid, import_errs = is_import_valid(file_path)

            EventLog.objects.log()

            if not import_valid:
                for err in import_errs:
                    messages.add_message(request, messages.ERROR, err)
                memport.delete()
                return redirect('membership_import_upload_file')

            return redirect('membership_import_preview', memport.id)
    else:
        form = UploadForm()

    return render_to_response(template_name, {
        'form': form,
        'datetime': datetime,
        }, context_instance=RequestContext(request))


@login_required
def membership_import_preview(request, id):
    """
    This will generate a form based on the uploaded CSV for field mapping.
    A preview will be generated based on the mapping given.
    """
    if not request.user.profile.is_superuser:
        raise Http403

    memport = get_object_or_404(MembershipImport, pk=id)

    if request.method == 'POST':
        form = ImportMapForm(request.POST, memport=memport)

        if form.is_valid():
            #show the user a preview based on the mapping
            cleaned_data = form.cleaned_data
            file_path = memport.get_file().file.name
            #file_path = os.path.join(settings.MEDIA_ROOT, memport.get_file().file.name)
            memberships, stats = parse_mems_from_csv(
                file_path,
                cleaned_data,
                membership_import=memport
            )

            EventLog.objects.log()

            # return the form to use it for the confirm view
            template_name = 'memberships/import-preview.html'
            return render_to_response(template_name, {
                'memberships': memberships,
                'stats': stats,
                'memport': memport,
                'form': form,
                'datetime': datetime,
            }, context_instance=RequestContext(request))

    else:
        form = ImportMapForm(memport=memport)

    template_name = 'memberships/import-map-fields.html'
    return render_to_response(template_name, {
        'form': form,
        'memport': memport,
        'datetime': datetime,
        }, context_instance=RequestContext(request))


@login_required
def membership_import_confirm(request, id):
    """
    Confirm the membership import and continue with the process.
    This can only be accessed via a hidden post form from the preview page.
    That will hold the original mappings selected by the user.
    """
    if not request.user.profile.is_superuser:
        raise Http403

    memport = get_object_or_404(MembershipImport, pk=id)

    if request.method == "POST":
        form = ImportMapForm(request.POST, memport=memport)

        if form.is_valid():
            cleaned_data = form.cleaned_data

            EventLog.objects.log()

            if not settings.CELERY_IS_ACTIVE:
                result = ImportMembershipsTask()
                memberships, stats = result.run(memport, cleaned_data)
                return render_to_response('memberships/import-confirm.html', {
                    'memberships': memberships,
                    'stats': stats,
                    'datetime': datetime,
                }, context_instance=RequestContext(request))
            else:
                result = ImportMembershipsTask.delay(memport, cleaned_data)

            # updates membership protection
            # uses setting on membership settings page
            call_command('membership_update_protection')

            return redirect('membership_import_status', result.task_id)
    else:
        return redirect('membership_import_preview', memport.id)


@login_required
def membership_import_status(request, task_id, template_name='memberships/import-confirm.html'):
    """
    Checks if a membership import is completed.
    """
    if not request.user.profile.is_superuser:
        raise Http403

    try:
        task = TaskMeta.objects.get(task_id=task_id)
    except TaskMeta.DoesNotExist:
        #tasks database entries are not created at once.
        task = None

    if task and task.status == "SUCCESS":

        memberships, stats = task.result

        return render_to_response(template_name, {
            'memberships': memberships,
            'stats': stats,
            'datetime': datetime,
        }, context_instance=RequestContext(request))
    else:
        return render_to_response('memberships/import-status.html', {
            'task': task,
            'datetime': datetime,
        }, context_instance=RequestContext(request))


@staff_member_required
def membership_join_report(request):
    now = datetime.now()
    mems = Membership.objects.all()
    mem_type = ''
    mem_stat = ''
    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['membership_type']:
                mem_type = form.cleaned_data['membership_type']
                mems = mems.filter(membership_type=form.cleaned_data['membership_type'])
            if form.cleaned_data['membership_status']:
                mem_stat = form.cleaned_data['membership_status']
                if form.cleaned_data['membership_status'] == 'ACTIVE':
                    mems = mems.filter(expire_dt__gte=now, subscribe_dt__lte=now)
                else:
                    mems = mems.exclude(expire_dt__gte=now, subscribe_dt__lte=now)
    else:
        form = ReportForm()
    mems30days = mems.filter(subscribe_dt__gte=now - timedelta(days=30))
    mems60days = mems.filter(subscribe_dt__gte=now - timedelta(days=60))
    mems90days = mems.filter(subscribe_dt__gte=now - timedelta(days=90))

    EventLog.objects.log()

    return render_to_response(
                'reports/membership_joins.html', {
                    'mems30days': mems30days,
                    'mems60days': mems60days,
                    'mems90days': mems90days,
                    'form': form,
                    'mem_type': mem_type,
                    'mem_stat': mem_stat,
                },
                context_instance=RequestContext(request))

@staff_member_required
@password_required
def membership_export(request):
    template_name = 'memberships/export.html'
    form = ExportForm(request.POST or None, user=request.user)

    if request.method == 'POST':
        if form.is_valid():
            # reset the password_promt session
            request.session['password_promt'] = False
            app = form.cleaned_data['app']
            export_id = run_export_task('memberships', 'membership', [], app)
            return redirect('export.status', export_id)

    return render_to_response(template_name, {
            'form': form
            }, context_instance=RequestContext(request))


@staff_member_required
def membership_join_report_pdf(request):
    now = datetime.now()
    days = request.GET.get('days', 30)
    mem_type = request.GET.get('mem_type', None)
    mem_stat = request.GET.get('mem_stat', None)
    mems = Membership.objects.all()
    if mem_type:
        mems = mems.filter(membership_type=mem_type)
    if mem_stat:
        if mem_stat == 'ACTIVE':
            mems = mems.filter(expire_dt__gte=now, subscribe_dt__lte=now)
        else:
            mems = mems.exclude(expire_dt__gte=now, subscribe_dt__lte=now)
    mems = mems.filter(subscribe_dt__gte=now - timedelta(days=int(days)))
    report = ReportNewMems(queryset=mems)
    resp = HttpResponse(mimetype='application/pdf')
    report.generate_by(PDFGenerator, filename=resp)

    EventLog.objects.log()

    return resp


@staff_member_required
def report_active_members(request, template_name='reports/membership_list.html'):

    mems = Membership.objects.filter(expire_dt__gt=datetime.now())

    # sort order of all fields for the upcoming response
    is_ascending_username = True
    is_ascending_full_name = True
    is_ascending_email = True
    is_ascending_app = True
    is_ascending_type = True
    is_ascending_subscription = True
    is_ascending_expiration = True
    is_ascending_invoice = True

    # get sort order
    sort = request.GET.get('sort', 'subscribe_dt')
    if sort == 'username':
        mems = mems.order_by('user__username')
        is_ascending_username = False
    elif sort == '-username':
        mems = mems.order_by('-user__username')
        is_ascending_username = True
    elif sort == 'full_name':
        mems = mems.order_by('user__first_name', 'user__last_name')
        is_ascending_full_name = False
    elif sort == '-full_name':
        mems = mems.order_by('-user__first_name', '-user__last_name')
        is_ascending_full_name = True
    elif sort == 'email':
        mems = mems.order_by('user__email')
        is_ascending_email = False
    elif sort == '-email':
        mems = mems.order_by('-user__email')
        is_ascending_email = True
    elif sort == 'app':
        mems = mems.order_by('ma')
        is_ascending_app = False
    elif sort == '-app':
        mems = mems.order_by('-ma')
        is_ascending_app = True
    elif sort == 'type':
        mems = mems.order_by('membership_type')
        is_ascending_type = False
    elif sort == '-type':
        mems = mems.order_by('-membership_type')
        is_ascending_type = True
    elif sort == 'subscription':
        mems = mems.order_by('subscribe_dt')
        is_ascending_subscription = False
    elif sort == '-subscription':
        mems = mems.order_by('-subscribe_dt')
        is_ascending_subscription = True
    elif sort == 'expiration':
        mems = mems.order_by('expire_dt')
        is_ascending_expiration = False
    elif sort == '-expiration':
        mems = mems.order_by('-expire_dt')
        is_ascending_expiration = True
    elif sort == 'invoice':
        # since we need to sort by a related field with the proper
        # conditions we'll need to bring the sorting to the python level
        for mem in mems:
            mem.valid_invoice = None
            if mem.get_entry():
                if mem.get_entry().invoice:
                    mem.valid_invoice = mem.get_entry().invoice.pk

        mems = sorted(mems, key=lambda mem: mem.valid_invoice, reverse=True)
        is_ascending_invoice = False
    elif sort == '-invoice':
        # since we need to sort by a related field with the proper
        # conditions we'll need to bring the sorting to the python level
        for mem in mems:
            mem.valid_invoice = None
            if mem.get_entry():
                if mem.get_entry().invoice:
                    mem.valid_invoice = mem.get_entry().invoice.pk

        mems = sorted(mems, key=lambda mem: mem.valid_invoice, reverse=False)
        is_ascending_invoice = True

    EventLog.objects.log()

    # returns csv response ---------------
    ouput = request.GET.get('output', '')
    if ouput == 'csv':

        table_header = [
            'username',
            'full name',
            'email',
            'application',
            'type',
            'subscription',
            'expiration',
        ]

        table_data = []
        for mem in mems:
            table_data = [
                mem.user.username,
                mem.user.get_full_name,
                mem.user.email,
                mem.ma.name,
                mem.membership_type.name,
                mem.subscribe_dt,
                mem.expire_dt,
            ]

        return render_csv(
            'active-memberships.csv',
            table_header,
            table_data,
        )
    # ------------------------------------

    return render_to_response(template_name, {
            'mems': mems,
            'active': True,
            'is_ascending_username': is_ascending_username,
            'is_ascending_full_name': is_ascending_full_name,
            'is_ascending_email': is_ascending_email,
            'is_ascending_app': is_ascending_app,
            'is_ascending_type': is_ascending_type,
            'is_ascending_subscription': is_ascending_subscription,
            'is_ascending_expiration': is_ascending_expiration,
            'is_ascending_invoice': is_ascending_invoice,
            }, context_instance=RequestContext(request))


@staff_member_required
def report_expired_members(request, template_name='reports/membership_list.html'):

    mems = Membership.objects.expired()

    # sort order of all fields for the upcoming response
    is_ascending_username = True
    is_ascending_full_name = True
    is_ascending_email = True
    is_ascending_app = True
    is_ascending_type = True
    is_ascending_subscription = True
    is_ascending_expiration = True
    is_ascending_invoice = True

    # get sort order
    sort = request.GET.get('sort', 'subscribe_dt')
    if sort == 'username':
        mems = mems.order_by('user__username')
        is_ascending_username = False
    elif sort == '-username':
        mems = mems.order_by('-user__username')
        is_ascending_username = True
    elif sort == 'full_name':
        mems = mems.order_by('user__first_name', 'user__last_name')
        is_ascending_full_name = False
    elif sort == '-full_name':
        mems = mems.order_by('-user__first_name', '-user__last_name')
        is_ascending_full_name = True
    elif sort == 'email':
        mems = mems.order_by('user__email')
        is_ascending_email = False
    elif sort == '-email':
        mems = mems.order_by('-user__email')
        is_ascending_email = True
    elif sort == 'application':
        mems = mems.order_by('ma')
        is_ascending_app = False
    elif sort == '-application':
        mems = mems.order_by('-ma')
        is_ascending_app = True
    elif sort == 'type':
        mems = mems.order_by('membership_type')
        is_ascending_type = False
    elif sort == '-type':
        mems = mems.order_by('-membership_type')
        is_ascending_type = True
    elif sort == 'subscription':
        mems = mems.order_by('subscribe_dt')
        is_ascending_subscription = False
    elif sort == '-subscription':
        mems = mems.order_by('-subscribe_dt')
        is_ascending_subscription = True
    elif sort == 'expiration':
        mems = mems.order_by('expire_dt')
        is_ascending_expiration = False
    elif sort == '-expiration':
        mems = mems.order_by('-expire_dt')
        is_ascending_expiration = True
    elif sort == 'invoice':
        # since we need to sort by a related field with the proper
        # conditions we'll need to bring the sorting to the python level
        for mem in mems:
            mem.valid_invoice = None
            if mem.get_entry():
                if mem.get_entry().invoice:
                    mem.valid_invoice = mem.get_entry().invoice.pk

        mems = sorted(mems, key=lambda mem: mem.valid_invoice, reverse=True)
        is_ascending_invoice = False
    elif sort == '-invoice':
        # since we need to sort by a related field with the proper
        # conditions we'll need to bring the sorting to the python level
        for mem in mems:
            mem.valid_invoice = None
            if mem.get_entry():
                if mem.get_entry().invoice:
                    mem.valid_invoice = mem.get_entry().invoice.pk

        mems = sorted(mems, key=lambda mem: mem.valid_invoice, reverse=False)
        is_ascending_invoice = True

    EventLog.objects.log()

    # returns csv response ---------------
    ouput = request.GET.get('output', '')
    if ouput == 'csv':

        table_header = [
            'username',
            'full name',
            'email',
            'application',
            'type',
            'subscription',
            'expiration',
        ]

        table_data = []
        for mem in mems:
            table_data = [
                mem.user.username,
                mem.user.get_full_name,
                mem.user.email,
                mem.ma.name,
                mem.membership_type.name,
                mem.subscribe_dt,
                mem.expire_dt,
            ]

        return render_csv(
            'expired-memberships.csv',
            table_header,
            table_data,
        )
    # ------------------------------------

    return render_to_response(template_name, {
            'mems': mems,
            'active': False,
            'is_ascending_username': is_ascending_username,
            'is_ascending_full_name': is_ascending_full_name,
            'is_ascending_email': is_ascending_email,
            'is_ascending_app': is_ascending_app,
            'is_ascending_type': is_ascending_type,
            'is_ascending_subscription': is_ascending_subscription,
            'is_ascending_expiration': is_ascending_expiration,
            'is_ascending_invoice': is_ascending_invoice,
            }, context_instance=RequestContext(request))


@staff_member_required
def report_members_summary(request, template_name='reports/membership_summary.html'):
    days = get_days(request)

    chart_data = prepare_chart_data(days)

    EventLog.objects.log()

    return render_to_response(template_name, {
                'chart_data': chart_data,
                'date_range': (days[0], days[-1]),
            }, context_instance=RequestContext(request))


@staff_member_required
def report_members_over_time(request, template_name='reports/membership_over_time.html'):
    stats = get_over_time_stats()

    EventLog.objects.log()

    return render_to_response(template_name, {
        'stats': stats,
    }, context_instance=RequestContext(request))


@staff_member_required
def report_members_stats(request, template_name='reports/membership_stats.html'):
    """Shows a report of memberships per membership type.
    """
    summary, total = get_membership_stats()

    EventLog.objects.log()

    return render_to_response(template_name, {
        'summary': summary,
        'total': total,
        }, context_instance=RequestContext(request))
