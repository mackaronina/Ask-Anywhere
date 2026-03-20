from django import template

from questions_answers.forms import CreateVoteQuestionForm

register = template.Library()


@register.inclusion_tag('questions_answers/question_card.html')
def question_card(question):
    return {'question': question}


@register.inclusion_tag('questions_answers/vote_block.html')
def question_vote_block(question, user):
    return {
        'entity': question,
        'user': user,
        'vote': question.get_vote(user),
        'vote_up_form': CreateVoteQuestionForm(initial={'is_positive': True}),
        'vote_down_form': CreateVoteQuestionForm(initial={'is_positive': False}),
        'delete_route': 'delete_vote_question',
        'create_route': 'create_vote_question',
    }


@register.inclusion_tag('questions_answers/question_tagging_block.html')
def question_tagging_block(question):
    return {
        'tags': question.tags.all(),
    }
