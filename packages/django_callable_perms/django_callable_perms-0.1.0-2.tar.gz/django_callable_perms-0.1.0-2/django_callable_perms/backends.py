# coding: utf-8


class PermissionRegistry(object):
    def __init__(self):
        self.perm_checks = {}
    
    def register(self, perm, check, model=None):
        key = (perm, model)
        if key in self.perm_checks:
            self.perm_checks[key].append(check)
        else:
            self.perm_checks[key] = [check]
    
    def get(self, perm, model=None):
        key = (perm, model)
        if key in self.perm_checks:
            return self.perm_checks[key]
        else:
            return []
registry = PermissionRegistry()


class CallablePermissionBackend(object):
    supports_object_permissions = True
    supports_anonymous_user = True
    supports_inactive_user = True
    registry = registry
    
    def authenticate(self):
        return None
    
    def has_perm(self, user, perm, obj=None):
        model = None
        if obj:
            model = obj.__class__
            while model._meta.proxy:
                model = model._meta.proxy_for_model
        
        # TODO: Caching?
        checks = self.registry.get(perm, model)
        for check in checks:
            if check(user, perm, obj):
                return True

