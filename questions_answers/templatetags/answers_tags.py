from django import template

from questions_answers.forms import MarkAnswerForm, CreateVoteAnswerForm

register = template.Library()


@register.inclusion_tag('questions_answers/answer_card.html')
def answer_card(answer):
    return {'answer': answer}


@register.inclusion_tag('questions_answers/edit_answer_block.html')
def edit_answer_block(question, answer, user):
    return {
        'question': question,
        'answer': answer,
        'user': user,
        'mark_answer_form': MarkAnswerForm(initial={'is_solution': True}),
        'unmark_answer_form': MarkAnswerForm(initial={'is_solution': False}),
    }


@register.inclusion_tag('questions_answers/vote_block.html')
def answer_vote_block(answer, user):
    return {
        'entity': answer,
        'user': user,
        'vote': answer.get_vote(user),
        'vote_up_form': CreateVoteAnswerForm(initial={'is_positive': True}),
        'vote_down_form': CreateVoteAnswerForm(initial={'is_positive': False}),
        'delete_route': 'delete_vote_answer',
        'create_route': 'create_vote_answer',
    }
