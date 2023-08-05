# Copyright 2010-2012 Canonical Ltd.  This software is licensed under
# the GNU Lesser General Public License version 3 (see the file LICENSE).

def audit_install():
    # import here to avoid triggering django imports during package import
    from django.contrib.admin import site
    from .models import AdminAuditMixin, AuditLog

    for model, model_admin in site._registry.items():
        if (model is AuditLog or isinstance(model_admin, AdminAuditMixin)):
            # Do not mingle with our own model
            continue
        site.unregister(model)
        new_model_admin = type('new_model_admin',
                               (AdminAuditMixin, model_admin.__class__),
                               model_admin.__dict__)
        site.register(model, new_model_admin)
