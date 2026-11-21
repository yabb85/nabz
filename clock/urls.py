from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('edit/', views.ClockEditView.as_view(), name='clock_list'),
    path('edit/<int:pk>', views.ClockEditView.as_view(), name='clock_list'),
    path("cron", views.cron, name='cron'),
    path('sound/<str:name>', views.sound, name='sound'),
]
