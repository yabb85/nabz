from django.contrib import admin
from .models import Bunny, ZStamp, Plugin

# Register your models here.
admin.site.register(Bunny)
admin.site.register(ZStamp)
admin.site.register(Plugin)
