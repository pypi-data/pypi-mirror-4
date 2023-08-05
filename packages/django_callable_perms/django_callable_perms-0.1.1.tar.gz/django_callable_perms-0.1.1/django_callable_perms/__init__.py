def register(perm, check, model=None):
    from django_callable_perms.backends import registry
    registry.register(perm, check, model)

