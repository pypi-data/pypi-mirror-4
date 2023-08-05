# Copyright 2010-2012 Canonical Ltd.  This software is licensed under
# the GNU Lesser General Public License version 3 (see the file LICENSE).

from operator import itemgetter

from django.conf import settings
from django.template import Context
from django.template.loader import get_template
from django.core.mail import send_mail


from adminaudit.management.commands import AdminAuditBaseCommand


class Command(AdminAuditBaseCommand):
    help = "Send out an email reporting the latest admin tasks performed."

    def handle(self, *args, **options):
        template = get_template("adminaudit/report.txt")

        recipients = getattr(settings, 'ADMINAUDIT_EMAILS_RECIPIENTS',
                             map(itemgetter(1), settings.ADMINS))
        subject = getattr(settings, 'ADMINAUDIT_SUMMARY_SUBJECT',
                          'Admin Audit Summary')
        from_email = getattr(settings, 'ADMINAUDIT_EMAIL_FROM',
                             settings.DEFAULT_FROM_EMAIL)

        if not recipients:
            print "No admin audit summary recipients configured."

        context = self.context_data()
        for recipient in recipients:
            context['recipient'] = recipient
            print "Sending e-email to", recipient,
            send_mail(subject, template.render(Context(context)),
                      from_email, [recipient], fail_silently=False)
            print " done"
