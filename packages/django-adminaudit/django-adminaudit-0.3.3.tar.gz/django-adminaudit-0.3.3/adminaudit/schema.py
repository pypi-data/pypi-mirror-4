# configglue schema to enable projects using configglue to use adminaudit
# this schema represents all adminaudit available configuration settings
from configglue.schema import (
    ListOption,
    Schema,
    Section,
    StringOption,
    )


class AdminAuditSchema(Schema):
    class adminaudit(Section):
        adminaudit_emails_recipients = ListOption(
            item=StringOption(),
            help='List of email addresss to send reports to.')
        adminaudit_summary_subject = StringOption(
            default='Admin Audit Summary',
            help='Email report subject.')
        adminaudit_email_from = StringOption(
            help='Email address from which to send reports.')
