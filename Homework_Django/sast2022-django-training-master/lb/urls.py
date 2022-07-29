from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.hello),
    path('leaderboard', views.leaderboard),
    path('history/<slug:user_name>',views.history),
    path('submit', views.submit),
    path('vote',views.vote)
    # 对应接口含义详见README.md
]
