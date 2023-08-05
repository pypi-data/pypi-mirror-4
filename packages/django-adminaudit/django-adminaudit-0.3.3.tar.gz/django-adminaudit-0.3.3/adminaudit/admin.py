# Copyright 2010-2012 Canonical Ltd.  This software is licensed under the
# GNU Lesser General Public License version 3 (see the file LICENSE).

from django.http import Http404
from django.contrib import admin
from django.utils import simplejson

from adminaudit.models import AuditLog


class AuditLogAdmin(admin.ModelAdmin):

    list_display = ('created_at', 'username', 'model', 'change')
    list_filter = ('username', 'created_at', 'change', 'model')

    def has_add_permission(self, request, obj=None):
        return False

    def delete_view(self, request, object_id, extra_context=None):
        raise Http404

    def change_view(self, request, object_id, extra_context=None):
        if request.method == 'POST':
            raise Http404
        audit_log = AuditLog.objects.get(pk=object_id)

        if extra_context is None:
            extra_context = {}

        if audit_log.change == 'update':
            decoded = simplejson.loads(audit_log.values)
            new_json = simplejson.dumps(decoded['new'], indent=2,
                                        sort_keys=True)
            old_json = simplejson.dumps(decoded['old'], indent=2,
                                        sort_keys=True)
            extra_context['new'] = new_json
            extra_context['old'] = old_json
        elif audit_log.change == 'delete':
            extra_context['new'] = ''
            extra_context['old'] = audit_log.values
        elif audit_log.change == 'create':
            extra_context['new'] = audit_log.values
            extra_context['old'] = ''

        return super(AuditLogAdmin, self).change_view(
            request, object_id, extra_context=extra_context)

    def get_actions(self, request):
        return []


admin.site.register(AuditLog, AuditLogAdmin)
