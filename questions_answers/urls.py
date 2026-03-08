from django.urls import path, include

from questions_answers import views
from questions_answers.views import RandomQuestion, CreateQuestion

urlpatterns = [
    path('', views.Index.as_view(), name='index'),
    path('questions/', include([
        path('', views.QuestionsIndex.as_view(), name='questions_index'),
        path('random/', RandomQuestion.as_view(), name='random_question'),
        path('create/', CreateQuestion.as_view(), name='create_question'),
        path('<uuid:pk>/', views.QuestionDetail.as_view(), name='question_detail'),
        path('<uuid:pk>/update/', views.UpdateQuestion.as_view(), name='update_question'),
        path('<uuid:pk>/delete/', views.DeleteQuestion.as_view(), name='delete_question'),
        path('<uuid:question_id>/answers/create/', views.CreateAnswer.as_view(), name='create_answer'),
    ])),
    path('answers/', include([
        path('<uuid:pk>/update/', views.UpdateAnswer.as_view(), name='update_answer'),
        path('<uuid:pk>/update/mark/', views.MarkAnswer.as_view(), name='update_answer_mark'),
        path('<uuid:pk>/delete/', views.DeleteAnswer.as_view(), name='delete_answer')
    ]))
]
