from django.contrib import admin

from questions_answers.models import Question, Answer, VoteAnswer, VoteQuestion

admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(VoteAnswer)
admin.site.register(VoteQuestion)
