from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('oneclick', views.one_click, name='oneclick'),
    path('doubleclick', views.double_click, name='doubleclick'),
    path('rfid', views.rfid, name='rfid'),
    path('sound/<str:name>', views.sound, name='sound'),
    path('edit/<int:pk>', views.WeatherEditView.as_view(), name='edit'),
]
