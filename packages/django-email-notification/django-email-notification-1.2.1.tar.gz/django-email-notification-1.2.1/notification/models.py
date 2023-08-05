# -*- coding: utf-8 -*-

import datetime
import operator
from hashlib import md5 as hash_md5

from smtplib import SMTPRecipientsRefused

from django.db import models
from django.conf import settings
from django.contrib.auth import models as auth_models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.contrib.sites.models import Site
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _


class GetAttrMixin(object):
    """Retrieve a Class from a path of this form: 'project.application.models.Model'."""
    def _get_class(self, path):
        return getattr(__import__(path.rsplit('.', 1)[0], fromlist=['']), path.rsplit('.', 1)[1])

    def _get_title_attr(self, instance, title_attr):
        """title_attr attribute of settings may be a callable."""
        attr = getattr(instance, title_attr)
        return attr() if callable(attr) else attr


class ModelWithMD5(models.Model):
    """Generate MD5 at creation."""
    md5 = models.CharField(max_length=32, editable=False)

    def save(self, *args, **kwargs):
        if not self.id:
            self.md5 = hash_md5(datetime.datetime.today().strftime('%f')).hexdigest()
        super(ModelWithMD5, self).save(*args, **kwargs)

    class Meta:
        abstract = True


class SimpleRegistrationRegistredManager(models.Manager):
    def get_query_set(self):
        return super(SimpleRegistrationRegistredManager, self
                ).get_query_set().exclude(unregistred=True).order_by('-registration_date')


class SimpleRegistration(ModelWithMD5):
    """Users who registered to notifications but are not Django users. Only email is required."""
    registration_date = models.DateTimeField(auto_now_add=True, verbose_name=_(u"Registration date"))
    email = models.EmailField(verbose_name=_(u"Email"))
    first_name = models.CharField(max_length=70, blank=True, verbose_name=_(u"First name"))
    last_name = models.CharField(max_length=70, blank=True, verbose_name=_(u"Name"))
    unregistred = models.BooleanField(default=False, verbose_name=_(u"Has unregistred"))

    objects = SimpleRegistrationRegistredManager()

    def __unicode__(self):
        return self.email

    class Meta:
        verbose_name = _(u"Registration")


class Item(models.Model, GetAttrMixin):
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    def _get_descr(self):
        for descr in settings.NOTIFICATION_ASSOCIATED_OBJECTS:
            if isinstance(self.content_object, self._get_class(descr['class'])):
                return descr

    def get_instance(self):
        Klass = self.content_type.model_class()
        return Klass.objects.get(id=self.object_id)

    def __unicode__(self):
        descr_dict = self._get_descr()
        if descr_dict:
            attr = getattr(self.content_object, descr_dict['title_attr'])
            title = attr() if callable(attr) else attr
            return "%s: %s" % (descr_dict['description'], title)
        else:
            # well it's ambarrassing, it seems we sometimes have wrong contentypes in bdd
            return '%d %s' % (self.object_id, self.content_type)


class RecipientGroup(models.Model):
    name = models.CharField(max_length=300, verbose_name=_(u"Name"))
    recipients = models.ManyToManyField(SimpleRegistration, verbose_name=_(u"Users"))

    def __unicode__(self):
        return u"%s (%d subscribers)" % (self.name, self.recipients.all().count())

    class Meta:
        verbose_name = _(u"Registred users group")
        verbose_name_plural = _(u"Registred users groups")


class Notification(ModelWithMD5, GetAttrMixin):
    creation_date = models.DateTimeField(auto_now_add=True, verbose_name=_(u"Creation date"))
    modification_date = models.DateTimeField(auto_now=True, verbose_name=_(u"Last modification date"))
    sent_date = models.DateTimeField(null=True, default=None, blank=True, verbose_name=_(u"Send date"))
    subject = models.CharField(max_length=100, verbose_name=_(u"Subject"))
    from_name = models.CharField(max_length=100, blank=True, default=settings.NOTIFICATION_FROM_NAME,
            verbose_name=_(u"Sender name"))
    from_email = models.CharField(max_length=100, blank=True, default=settings.NOTIFICATION_FROM_EMAIL,
            verbose_name=_(u"Sender email"))
    body = models.TextField(verbose_name=_(u"Body"), blank=True)
    items = models.ManyToManyField(Item, blank=True, null=True, verbose_name=_(u"Linked objects"))
    recipient_groups = models.ManyToManyField(RecipientGroup, blank=True, null=True,
            verbose_name=_(u"Registred users groups"))
    registered_recipients = models.ManyToManyField(auth_models.User, blank=True, null=True,
            verbose_name=_(u"Site users"))
    recipients = models.ManyToManyField(SimpleRegistration, blank=True, null=True,
            verbose_name=_(u"Registed users"))
    template = models.CharField(choices=[], max_length=300)

    def __unicode__(self):
        return "%s (%s)" % (self.subject, self.creation_date)

    def all_recipients(self):
        """Aggregate and make unique."""
        recipients = [list(r.recipients.all()) for r in self.recipient_groups.all()]
        if recipients:
            recipients = reduce(operator.add, recipients)
        recipients = set(recipients) | set(self.recipients.all())
        recipients = list(recipients) + list(self.registered_recipients.all())
        return recipients

    def get_context(self, user=None):
        """Build email context, containing linked objects."""
        context = {}
        context['site'] = Site.objects.get(id=settings.SITE_ID)
        context['subject'] = self.subject
        context['body'] = self.body
        context['from_name'] = self.from_name
        context['from_mail'] = self.from_email
        context['notification'] = self
        context['object_types'] = {}

        # possible optimisation here
        for item in self.items.all():
            Klass = item.content_type.model_class()
            for object_type in settings.NOTIFICATION_ASSOCIATED_OBJECTS:
                if self._get_class(object_type['class']) == Klass:
                    if object_type['name'] not in context['object_types'].keys():
                        context['object_types'][object_type['name']] = {}
                        context['object_types'][object_type['name']]['long_description'] = object_type['long_description']
                        context['object_types'][object_type['name']]['instances'] = []
                    instance = Klass.objects.get(id=item.object_id)
                    instance.item = item
                    context['object_types'][object_type['name']]['instances'].append(instance)
        return context

    def get_sender(self):
        if self.from_email:
            if self.from_name:
                sender = "%s<%s>" % (self.from_name, self.from_email)
            else:
                sender = self.from_email
        else:
            sender = settings.NOTIFICATION_FROM_EMAIL
        return sender

    def send_emails(self, fail_silently=False):
        """Send the emails..."""

        template = 'email'
        context = self.get_context()
        for recipient in self.all_recipients():
            context['recipient'] = recipient
            text_content = render_to_string('notification/emails/' + template + '.txt', context)
            html_content = render_to_string('notification/emails/' + template + '.html', context)
            email = EmailMultiAlternatives(
                    subject=self.subject,
                    body=text_content,
                    from_email=self.get_sender(),
                    to=[recipient.email],
                )
            email.attach_alternative(html_content, "text/html")
            try:
                email.send()
            except SMTPRecipientsRefused:
                # TODO: log wrong email address
                pass

        self.sent_date = datetime.datetime.now()
        self.save()


class Hit(models.Model):
    """Record for statistics links clicked by recipients."""
    notification = models.ForeignKey(Notification, verbose_name=_(u"Notification"))
    item = models.ForeignKey(Item, verbose_name=_(u"Item"))
    recipient = models.ForeignKey(SimpleRegistration, verbose_name=_(u"Recipient"))
    hit_date = models.DateTimeField(default=datetime.datetime.now, verbose_name=_(u"Hit date"))
    count = models.PositiveIntegerField(default=1, verbose_name=_(u'Hits count'))

    class Metal:
        verbose_name = _(u"Hit")
        verbose_name_plural = _(u"Hits")

    def __unicode__(self):
        return u"%s-%s-%s %s" % (self.notification, self.item, self.recipient, self.hit_date)


# not used yet
class EmailLogEntry(models.Model):
    """Model to queue email to send and log sent one."""
    SUBJECT_MAX_LENGTH = 78

    _subject = models.CharField(max_length=SUBJECT_MAX_LENGTH)
    body = models.TextField()
    from_email = models.CharField(max_length=75)
    to = models.TextField()
    sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _(u"Email log entry")
        verbose_name_plural = _(u"Email log entries")

    def __unicode__(self):
        return u'%s / %s' % (self.to, self.sent_at)

    def get_subject(self):
        return self._subject

    def set_subject(self, value):
        if len(value) > EmailLogEntry.SUBJECT_MAX_LENGTH:
            self._subject = value[:EmailLogEntry.SUBJECT_MAX_LENGTH - 3] + '...'
        else:
            self._subject = value

    subject = property(get_subject, set_subject)
