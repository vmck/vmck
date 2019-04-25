from django.contrib import admin
from .models import Job, Upload, Source, Artifact
from django.urls import path

class Admin(admin.ModelAdmin):
	pass

admin.site.register(Job, Admin)
admin.site.register(Upload, Admin)
admin.site.register(Source, Admin)
admin.site.register(Artifact, Admin)

urlpatterns = [ 
	path('admin/', admin.site.urls)
]

