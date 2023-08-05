# -*- coding: utf-8 -*-

from django import forms
from django.conf import settings
from django.contrib import admin
from django.contrib.contenttypes.models import ContentType

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from .models import SimpleRegistration, Notification, RecipientGroup, Hit, GetAttrMixin, Item


def registered(obj):
    if not obj.unregistred:
        return '<img alt="True" src="%simg/admin/icon-yes.gif">' % (
                settings.ADMIN_MEDIA_PREFIX)
    else:
        return '<img alt="False" src="%simg/admin/icon-no.gif">' % settings.ADMIN_MEDIA_PREFIX
registered.allow_tags = True
registered.short_description = _("Registred")


class SimpleRegistrationAdmin(admin.ModelAdmin):
    list_display = ['registration_date', 'email', registered]
admin.site.register(SimpleRegistration, SimpleRegistrationAdmin)


admin.site.register(RecipientGroup)


class HitAdmin(admin.ModelAdmin):
    list_display = ['hit_date', 'notification', 'item', 'recipient']
admin.site.register(Hit, HitAdmin)


class DynFieldMixin(GetAttrMixin):

    def init_dynamic_fields(self):
        """Initialize form."""
        if self.instance.id:
            for item in self.instance.items.all():
                for object_type in settings.NOTIFICATION_ASSOCIATED_OBJECTS:
                    if self._get_class(object_type['class']) == item.content_type.model_class():
                        if object_type['name'] not in self.initial:
                            self.initial[object_type['name']] = []
                        self.initial[object_type['name']].append(item.object_id)

    def dynamic_fields(self):
        """Returns form fields for linkable objects."""
        fields = {}
        for object_type in settings.NOTIFICATION_ASSOCIATED_OBJECTS:
            C = self._get_class(object_type['class'])
            if object_type['manager']:
                objects_manager = getattr(C.objects, object_type['manager'])
            else:
                objects_manager = getattr(C.objects, 'all')
            choices = [(o.id, self._get_title_attr(o, object_type['title_attr']))
                    for o in objects_manager().order_by(object_type['order_by'])]
            fields[object_type['name']] = forms.MultipleChoiceField(choices=choices,
                    label=object_type['description'],
                    required=False)
        return fields

    def get_all_fields(self):
        all_fields = self.fields.copy()
        all_fields.update(self.dynamic_fields())
        return all_fields

    def save_dynamic_fields(self, commit=True):
        """Save linked objects."""

        self.instance.items.clear()
        for object_type in settings.NOTIFICATION_ASSOCIATED_OBJECTS:
            C = self._get_class(object_type['class'])
            ct = ContentType.objects.get_for_model(C)
            if len(self.cleaned_data[object_type['name']]):
                for id in self.cleaned_data[object_type['name']]:
                    item = Item.objects.create(content_type=ct,
                            object_id=id,
                    )
                    self.instance.items.add(item)
        self.instance.save()
        return self.instance


class NotificationFormAdmin(forms.ModelForm, DynFieldMixin):

    def __init__(self, *args, **kwargs):
        super(NotificationFormAdmin, self).__init__(*args, **kwargs)
        self.init_dynamic_fields()

    def save(self, *args, **kwargs):
        super(NotificationFormAdmin, self).save(*args, **kwargs)
        self.instance.save()
        self.save_dynamic_fields()
        return self.instance

    class Meta:
        model = Notification
        fields = ('subject', 'from_name', 'from_email', 'body', 'recipient_groups', 'registered_recipients', 'recipients')


def preview_link(obj):
    return '<a href="%s">Preview</a>' % reverse('view_notification', args=[obj.md5])
preview_link.allow_tags = True


class NotificationAdmin(admin.ModelAdmin):
    list_display = ['subject', 'body', 'creation_date', 'from_name', 'from_email', preview_link]
    ordering = ['-creation_date']
    search_fields = ['subject', 'body']

    def get_form(self, request, obj=None, **kwargs):
        """Inherit a new pure ModelForm from NotificationFormAdmin including dynamicaly created fields."""
        form = NotificationFormAdmin()
        new_form = type('NotificationFormAdmin', (NotificationFormAdmin, ), form.get_all_fields())
        return new_form

    def save_model(self, request, obj, form, change):
        super(NotificationAdmin, self).save_model(request, obj, form, change)
        if 'save-and-send' in request.POST:
            form.save_m2m()  # slightly anticipate m2m saving
            obj.send_emails()

admin.site.register(Notification, NotificationAdmin)
