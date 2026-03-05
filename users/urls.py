from django.contrib.auth.views import LogoutView
from django.urls import path, include

from users import views

app_name = 'users'
urlpatterns = [
    path('login/', views.LoginUser.as_view(), name='login'),
    path('signup/', views.SignupUser.as_view(), name='signup'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', include([
        path('', views.ProfileDetail.as_view(), name='profile'),
        path('update/', views.UpdateProfile.as_view(), name='update_profile'),
        path('delete/', views.DeleteProfile.as_view(), name='delete_profile')
    ])),
    path('<uuid:pk>/', views.UserDetail.as_view(), name='user_detail')
]
