from django.contrib.auth.views import LogoutView
from django.urls import path, include

from users import views

app_name = 'users'
urlpatterns = [
    path('login/', views.LoginUser.as_view(), name='login'),
    path('signup/', views.SignupUser.as_view(), name='signup'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('password-change/', views.PasswordChangeProfile.as_view(), name='password_change'),
    path('password-change/done/', views.PasswordChangeDoneProfile.as_view()),
    path('password-reset/', views.PasswordResetProfile.as_view(), name='password_reset'),
    path('password-reset/done/', views.PasswordResetDoneProfile.as_view(), name='password_reset_done'),
    path('password-reset/<uidb64>/<token>/', views.PasswordResetConfirmProfile.as_view(),
         name='password_reset_confirm'),
    path('password-reset/complete/', views.PasswordResetCompleteProfile.as_view(), name='password_reset_complete'),
    path('profile/', include([
        path('', views.ProfileDetail.as_view(), name='profile'),
        path('update/', views.UpdateProfile.as_view(), name='update_profile'),
        path('delete/', views.DeleteProfile.as_view(), name='delete_profile')
    ])),
    path('<uuid:pk>/', include([
        path('', views.UserDetail.as_view(), name='user_detail'),
        path('questions/', views.UserQuestionsList.as_view(), name='user_questions_list'),
        path('answers/', views.UserAnswersList.as_view(), name='user_answers_list'),
    ]))
]
