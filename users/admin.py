from django.contrib import admin
from django_restful_admin import site
from . import models

admin.site.register(models.User)
admin.site.register(models.LoginSession)
admin.site.register(models.UserDevice)
site.register(models.User)
site.register(models.LoginSession)
site.register(models.UserDevice)
