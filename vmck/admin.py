from django.contrib import admin
from .models import Job, Artifact, Upload, Source

admin.site.register(Job)
admin.site.register(Upload)
admin.site.register(Source)
admin.site.register(Artifact)