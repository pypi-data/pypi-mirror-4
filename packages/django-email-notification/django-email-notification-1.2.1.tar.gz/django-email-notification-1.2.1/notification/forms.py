# -*- coding: utf-8 -*-

from django import forms

from .models import SimpleRegistration

from .admin import NotificationFormAdmin


class NotificationForm(NotificationFormAdmin):
    def __init__(self, *args, **kwargs):
        super(NotificationForm, self).__init__(*args, **kwargs)
        self.fields = self.get_all_fields()


class SimpleRegistrationForm(forms.ModelForm):
    def save(self):   # prevent doubles
        super(SimpleRegistrationForm, self).save()
        if not SimpleRegistration.objects.filter(email=self.cleaned_data['email']).exists():
            return super(SimpleRegistrationForm, self).save()
        return False

    class Meta:
        model = SimpleRegistration
        fields = ['email']
