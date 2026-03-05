from django import template

register = template.Library()


@register.inclusion_tag('questions_answers/answer_card.html')
def answer_card(answer):
    return {'answer': answer}
