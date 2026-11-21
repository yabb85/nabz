from django.urls import path

from . import views

urlpatterns = [
    path('locate.jsp', views.locate, name='locate'),
    path('bc.jsp', views.bc, name='bc'),
    path('rfid.jsp', views.rfid, name='rfid'),
    path('record.jsp', views.record, name='record'),
    path('itmode.jsp', views.itmode, name='itmode'),
    path('order', views.order, name='order'),
    path('oneclick', views.one_click, name='oneclick'),
    path('doubleclick', views.double_click, name='doubleclick'),
    path('earsmove', views.ears_move, name='earsmove'),
    path('mp3/<str:filename>', views.mp3, name='mp3'),
    path("bunny", views.bunny, name="bunny"),
    path("bunny/details/<str:sn>", views.BunnyEditView.as_view(), name="bunny_details"),
    path("bunny/create", views.bunny_create, name="create"),
    path("zstamp", views.zstamp, name='zstamps'),
    path("zstamp/details/<str:sn>", views.ZstampEditView.as_view(), name='zstamps_details'),
    path("plugin", views.plugin, name="plugin"),
]
