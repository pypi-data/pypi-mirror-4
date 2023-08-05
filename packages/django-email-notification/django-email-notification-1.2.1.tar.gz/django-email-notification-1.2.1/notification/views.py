# -*- coding: utf-8 -*-

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.shortcuts import redirect, render, get_object_or_404
from django.utils.translation import ugettext as _
from django.views.decorators.http import require_POST

from .forms import SimpleRegistrationForm, NotificationForm
from .models import Notification, SimpleRegistration, Item, Hit


@require_POST
def register(request):
    """View to register non django users."""
    form = SimpleRegistrationForm(data=request.POST)
    if form.is_valid():
        if form.save():
            messages.add_message(request, messages.INFO, _(u"Your registration has been recorded"),
                    extra_tags=settings.NOTIFICATION_REGISTRATION_MESSAGE_TAG)
        else:
            messages.add_message(request, messages.WARNING, _(u"You are already registred"),
                    extra_tags=settings.NOTIFICATION_REGISTRATION_MESSAGE_TAG)
    else:
        messages.add_message(request, messages.ERROR, _(u"This email address is invalid"),
                    extra_tags=settings.NOTIFICATION_REGISTRATION_MESSAGE_TAG)
    return redirect(request.POST.get('next') or '/')


def unregister(request, md5):
    try:
        simple_registration = SimpleRegistration.objects.get(md5=md5)
        simple_registration.unregistred = True
        simple_registration.save()
        messages.add_message(request, messages.INFO, _(u"You have been unregistred"),
                extra_tags=settings.NOTIFICATION_REGISTRATION_MESSAGE_TAG)
    except SimpleRegistration.DoesNotExist:
        pass
    return redirect(settings.NOTIFICATION_UNSUBSCRIBE_REDIRECT or '/')


@login_required
def edit_notification(request, notification_id=None, instance=None):
    if notification_id:
        instance = get_object_or_404(Notification, id=notification_id)
    form = NotificationForm(instance=instance, data=request.POST or None)
    if form.is_valid():
        notification = form.save()
        if request.POST['submit'] == 'send':
            notification.send_emails()
        return redirect('/admin/notification/notification/')  # TODO add a setting for the post POST redirection
        #return redirect(reverse('notification_list'))
    return render(request, "notification/edit_notification.html", {
            'form': form,
    })


def view_notification(request, md5):
    try:
        notification = Notification.objects.get(md5=md5)
    except Notification.DoesNotExist:
        raise Http404

    template = 'email'
    context = notification.get_context()
    context['online'] = True
    return render(request, 'notification/emails/' + template + '.html',
            context)


@login_required
def notification_list(request):
    notifications = Notification.objects.all().order_by('-creation_date')
    return render(request, "notification/notification_list.html", {
            'notifications': notifications,
    })


def track_link(request, notification_md5, item_pk, recipient_md5):
    try:
        notification = Notification.objects.get(md5=notification_md5)
        item = Item.objects.get(pk=item_pk)
        recipient = SimpleRegistration.objects.get(md5=recipient_md5)
    except ObjectDoesNotExist:
        return redirect('/')
    hit, created = Hit.objects.get_or_create(notification=notification,
            item=item,
            recipient=recipient)
    if not created:
        hit.count += 1
        hit.save()
    return redirect(item.get_instance().get_absolute_url())
