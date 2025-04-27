from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),  
    path('quiz_home/', views.quiz_home, name='quiz_home'),  
    path('quiz/<int:category_id>/<int:difficulty_id>/', views.quiz, name='quiz'),
    path('top-scorers/', views.top_scorers, name='top_scorers'),
    path('feedback/', views.feedback, name='feedback'),
    path('profile/', views.profile, name='profile'),
    path('results/', views.results, name='results'),  
    path('logout/', views.logout_view, name='logout'),
]

