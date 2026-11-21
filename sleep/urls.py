from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('cron', views.cron, name='cron'),
    path('oneclick', views.one_click, name='oneclick'),
    path('doubleclick', views.double_click, name='doubleclick'),
    path('sound/<str:name>', views.sound, name='sound'),
    path('edit/<str:sn>', views.SleepEditView.as_view(), name='index'),
]
