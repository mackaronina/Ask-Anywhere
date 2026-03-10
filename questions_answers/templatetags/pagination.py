from django import template

register = template.Library()


@register.inclusion_tag('questions_answers/pagination_block.html')
def pagination_block(paginator, page_obj):
    return {'paginator': paginator, 'page_obj': page_obj}
