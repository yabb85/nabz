from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('record', views.record, name='record'),
    # path('cron', views.cron, name='cron'),
    path('oneclick', views.one_click, name='oneclick'),
    path('doubleclick', views.double_click, name='doubleclick'),
    path('earsmove', views.ears_move, name='earsmove'),
    path('sound/<str:name>', views.sound, name='sound'),
]
