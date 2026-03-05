from django import template

register = template.Library()


@register.inclusion_tag('users/user_link.html')
def user_link(user):
    return {'user': user}
