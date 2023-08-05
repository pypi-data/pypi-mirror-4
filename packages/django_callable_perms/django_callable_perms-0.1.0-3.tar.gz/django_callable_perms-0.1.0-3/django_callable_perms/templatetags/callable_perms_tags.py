# -*- coding: utf-8 -*-
from django import template
from django_callable_perms.template import PermissionAccess

register = template.Library()

class ObjectPermissionsNode(template.Node):
    def __init__(self, user, obj, as_var):
        self.user = user
        self.obj = obj
        self.as_var = as_var
    
    def render(self, context):
        # TODO: Test if self.as_var already in context, reuse if possible (has same details)
        try:
            obj = self.obj.resolve(context)
            user = self.user.resolve(context)
        except template.VariableDoesNotExist:
            return ''
        context[self.as_var] = PermissionAccess(user, obj)
        return ''

@register.tag
def get_obj_perms(parser, token):
    """
    {% get_obj_perms for user accessing obj as var %}
    """
    tokens = token.split_contents()
    tag_name = tokens[0]
    values = tokens[1:]
    if len(values) != 6:
        raise template.TemplateSyntaxError("%r tag requires five arguments ('for request.user accessing obj as var')" % tag_name)
    if values[0] != 'for':
        raise template.TemplateSyntaxError("%r tag first argument must be 'for'" % tag_name)
    if values[2] != 'accessing':
        raise template.TemplateSyntaxError("%r tag third argument must be 'accessing'" % tag_name)
    if values[4] != 'as':
        raise template.TemplateSyntaxError("%r tag fifth argument must be 'as'" % tag_name)
    user = parser.compile_filter(values[1])
    obj = parser.compile_filter(values[3])
    as_var = values[5]
    return ObjectPermissionsNode(user, obj, as_var)

