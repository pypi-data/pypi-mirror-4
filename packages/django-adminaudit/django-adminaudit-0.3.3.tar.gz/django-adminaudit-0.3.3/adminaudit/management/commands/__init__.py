# Copyright 2010-2012 Canonical Ltd.  This software is licensed under
# the GNU Lesser General Public License version 3 (see the file LICENSE).

from datetime import date, timedelta, time, datetime

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from adminaudit.models import AuditLog


class AdminAuditBaseCommand(BaseCommand):

    def data_for_user(self, user_id, auditlogs):
        username = User.objects.get(pk=user_id).username
        caption = "{0}'s changes".format(username)
        return {
            'auditlogs': auditlogs.filter(user_id=user_id),
            'caption': caption,
            'underline': "=" * len(caption),
        }

    def report_date(self):
        return date.today() - timedelta(days=1)

    def context_data(self):
        yesterday = self.report_date()

        auditlogs = AuditLog.objects.filter(created_at__range=(
            yesterday, datetime.combine(yesterday, time.max)))

        users = []
        for value in auditlogs.values('user_id').distinct():
            users.append(self.data_for_user(value['user_id'], auditlogs))

        return {
            'report_for_date': yesterday,
            'users': users,
        }
