
from optparse import make_option

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from ...models import Notification

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-n', '--notification',
            action='store',
            type='int',
            dest='notification_id',
            default=None,
            help='The notification to send'),
        make_option('-d', '--debug',
            action='store_true',
            dest='debug',
            default=None,
            help='Output emails to stdout'),
    )
    help = "Command to send emails"

    def handle(self, *args, **options):
        try:
            notification = Notification.objects.get(id=options.get('notification_id'))
        except Notification.DoesNotExist:
            raise CommandError("Specify a valid notification ID")
        output = u"Notification #{0}: \nSubject: {1}\nRecipients: {2}\n\n".format(
                notification.id,
                notification.subject,
                len(notification.all_recipients()))
        self.stdout.write(output.encode(self.stdout.encoding))
        notification.send_emails()

