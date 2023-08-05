# Copyright 2010-2012 Canonical Ltd.  This software is licensed under
# the GNU Lesser General Public License version 3 (see the file LICENSE).

from django.template import Context
from django.template.loader import get_template

from adminaudit.management.commands import AdminAuditBaseCommand


class Command(AdminAuditBaseCommand):

    help = "Report the latest admin tasks performed."

    def handle(self, *args, **kwargs):
        template = get_template("adminaudit/report.txt")
        context = Context(self.context_data())

        print template.render(context)
