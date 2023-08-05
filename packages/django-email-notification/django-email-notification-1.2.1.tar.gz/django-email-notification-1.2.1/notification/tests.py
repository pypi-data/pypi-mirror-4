# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core import mail
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client

from app.models import Product, Information

from .forms import NotificationForm, SimpleRegistrationForm
from .models import SimpleRegistration, Notification, Item


class BaseTest(TestCase):
    def setUp(self):
        # create some object to link to the notificaiton
        self.products = []
        self.informations = []
        for i in xrange(1):
            self.products.append(Product.objects.create(name=u"Product #%d" % i))
            self.informations.append(Information.objects.create(title=u"Information #%d" % i))

        # create Django user
        self.user = User.objects.create(username='admin', email='user@example.com',
                is_staff=True, is_active=True, is_superuser=True)
        self.user.set_password('admin')
        self.user.save()

        # create registered user
        self.ruser1 = SimpleRegistration.objects.create(email='ruser@example.com')
        self.ruser2 = SimpleRegistration.objects.create(email='user@example.com')  # same email that user
        self.client = Client()
        self.client.login(username='admin', password='admin')


class NotificationTest(BaseTest):

    def test_notification_form(self):
        """Ensure linked object like Product are correctly converted into generic relation (items)."""
        form = NotificationForm()
        self.assertIn('products', form.fields)
        self.assertNotIn('items', form.fields)

        data = {'subject': u"notif 1",
                'products': [self.products[0].pk]
                }
        form = NotificationForm(data=data)
        notification = form.save()
        item = notification.items.all()[0]
        self.assertTrue(item.pk == self.products[0].pk)
        self.assertTrue(item.content_type.model_class() == Product)

    def test_notification_send(self):
        """Send notification."""
        # create a notification using form
        data = {'subject': u"notif 1",
                'products': [self.products[0].pk],
                'informations': [self.informations[0].pk],
                'from_name': 'test',
                'from_email': 'test@example.com',
                'body': 'from test with love',
                'registered_recipients': [self.user.pk],
                'recipients': [self.ruser1.pk],
                }
        form = NotificationForm(data=data)
        notification = form.save()
        notification.send_emails()
        self.assertTrue(len(mail.outbox), 2)

    def test_notification_send_duplicate(self):
        """Test only one mail is sent for duplicate emails."""
        #create a notification using model
        data = {'subject': u"notif 1",
                'from_name': 'test',
                'from_email': 'test@example.com',
                'body': 'from test with love',
                }
        notification = Notification.objects.create(**data)
        notification.registered_recipients = [self.user]
        notification.recipients = [self.ruser2]  # self.user and self.ruser2 have same emails
        notification.items = [Item.objects.create(
                content_type=ContentType.objects.get(app_label='app', model='product'),
                object_id=self.products[0].pk)]
        notification.save()
        notification.send_emails()
        self.assertTrue(len(mail.outbox), 1)


class TestSimpleRegistration(TestCase):

    def test_form(self):
        email = 'someone@example.com'
        data = {'email': email}
        form = SimpleRegistrationForm(data=data)
        form.save()
        self.assertTrue(SimpleRegistration.objects.filter(email=email).count() == 1)

        self.assertFalse(form.save())  # no duplicate allowed, should return False
        self.assertTrue(SimpleRegistration.objects.filter(email=email).count() == 1)

    def test_unregistration(self):
        """Ensure unregistred users are not selectable."""
        email = 'someoneelse@example.com'
        user = SimpleRegistration.objects.create(email=email)
        self.assertTrue(SimpleRegistration.objects.filter(email=email).count() == 1)
        user.unregistred = True
        user.save()
        self.assertTrue(SimpleRegistration.objects.filter(email=email).count() == 0)


class TestAdmin(BaseTest):
    """Test Django admin integration."""
    def test_add(self):
        url = reverse('admin:notification_notification_add')
        response = self.client.get(url)
        self.assertContains(response, '<input type="submit" name="save-and-send"')  # our send button
        self.assertContains(response, '<select multiple="multiple" name="products"')
        self.assertContains(response, '<option value="1">Product #0</option>')

        subject = u"admin_notif"
        data = {'subject': subject,
                'products': [self.products[0].pk],
                'informations': [self.informations[0].pk],
                'from_name': 'test',
                'from_email': 'test@example.com',
                'body': 'from test with love',
                'registered_recipients': [self.user.pk],
                'recipients': [self.ruser1.pk],
                'save-and-send': 1,
                }
        response = self.client.post(url, data, follow=True)
        notification = Notification.objects.get(subject=subject)
        self.assertTrue(notification.recipients.count() == 1)
        self.assertTrue(notification.registered_recipients.count() == 1)
        self.assertTrue(notification.items.count() == 2)
        self.assertTrue(len(mail.outbox) == 2)

    def test_change(self):
        #create a notification using model
        data = {'subject': u"notif 1",
                'from_name': 'test',
                'from_email': 'test@example.com',
                'body': 'from test with love',
                }
        notification = Notification.objects.create(**data)
        notification.items = [Item.objects.create(
                content_type=ContentType.objects.get(app_label='app', model='product'),
                object_id=self.products[0].pk)]
        notification.save()
        url = reverse('admin:notification_notification_change', args=[notification.pk])
        data.update({
                'registered_recipients': [self.user.pk],
                'recipients': [self.ruser1.pk],
                'save-and-send': 1,
                })
        self.client.post(url, data, follow=True)
        self.assertTrue(len(mail.outbox) == 2)
