from django.contrib import admin
from django.urls import path, include
from . import api
from . import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("v0/", include(api.urls)),
    path("", views.homepage),
]
