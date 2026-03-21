from django.urls import path, include

from questions_answers import views
from questions_answers.views import RandomQuestion, CreateQuestion

urlpatterns = [
    path('', views.Index.as_view(), name='index'),
    path('questions/', include([
        path('', views.QuestionsIndex.as_view(), name='questions_index'),
        path('random/', RandomQuestion.as_view(), name='random_question'),
        path('create/', CreateQuestion.as_view(), name='create_question'),
        path('<uuid:pk>/', include([
            path('', views.QuestionDetail.as_view(), name='question_detail'),
            path('update/', views.UpdateQuestion.as_view(), name='update_question'),
            path('delete/', views.DeleteQuestion.as_view(), name='delete_question'),
            path('votes/create/', views.CreateVoteQuestion.as_view(), name='create_vote_question'),
            path('votes/delete/', views.DeleteVoteQuestion.as_view(), name='delete_vote_question'),
            path('answers/create/', views.CreateAnswer.as_view(), name='create_answer'),
        ]))
    ])),
    path('answers/<uuid:pk>/', include([
        path('update/', views.UpdateAnswer.as_view(), name='update_answer'),
        path('update/mark/', views.MarkAnswer.as_view(), name='update_answer_mark'),
        path('delete/', views.DeleteAnswer.as_view(), name='delete_answer'),
        path('votes/create/', views.CreateVoteAnswer.as_view(), name='create_vote_answer'),
        path('votes/delete/', views.DeleteVoteAnswer.as_view(), name='delete_vote_answer'),
    ]))
]
