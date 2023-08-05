============
Notification
============

Notifications are short emails sent to users by Facebook or Twitter to inform users of some changes.

django-email-notification allows backoffice users to send short email notifications to django registered users or users you only know the email about what is new or changed from django's admin or a dedicated view. And then track their clicks.


settings:
---------
::

    NOTIFICATION_FROM_EMAIL = ''  # sender email, typically no-reply@you-site.com
    NOTIFICATION_FROM_NAME = ''   # sender name
    NOTIFICATION_UNSUBSCRIBE_REDIRECT = '/you-unsubscribed/'  # possible page redirection after unsubscription
    NOTIFICATION_REGISTRATION_MESSAGE_TAG = 'notification'  # allow filtering notification messages

    # Description of linkable objects.
    NOTIFICATION_ASSOCIATED_OBJECTS = (
        {   'name': 'products',                                     # reference name, used in forms and templates
            'description': u"New products",                         # Human readable description
            'long_description': u"Last products added to our site", # Long description
            'class': 'project.application.models.Product',          # path to the class model
            'title_attr': 'product_description',                    # Model instance field or callable to display in form
            'order_by': '-creation_date',                           # order to sort Model instances in form and email template
            'manager': '',                                          # manager to use if so
        },
    )


Email template:
---------------

In template, linked objects can be processed this way by example:
::

    {% if object_types.OBJECT_NAME.instances %}
        <ul><li>{{ object_types.OBJECT_NAME.long_description }}
        <ul>{% for instance in object_types.OBJECT_NAME.instances %}
        <li>{% include 'notification/emails/tracked_link.html' %}</li>
        {% endfor %}</ul>
        </li></ul>
    {% endif %}

Messages sent through the django messages framework filtered like this:
::

    {% if messages %}
        {% for message in messages %}
            {% if 'notification' in message.tags %}
                <span class="email-registration-message lvl-{{ message.level }}">{{ message }}</span>
            {% endif %}
        {% endfor %}
    {% endif %}
