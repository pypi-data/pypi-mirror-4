class ObjectPermissions(object):
    def __init__(self, user, obj, module_name):
        self.user = user
        self.obj = obj
        self.module_name = module_name

    def __getitem__(self, perm_name):
        return self.user.has_perm("%s.%s" % (self.module_name, perm_name), self.obj)


class PermissionAccess(object):
    def __init__(self, user, obj):
        self.user = user
        self.obj = obj

    def __getitem__(self, module_name):
        return ObjectPermissions(self.user, self.obj, module_name)

