from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('cron', views.cron, name='cron'),
    path('sound/', views.sound, name='sound'),
]
