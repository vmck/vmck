import json
from django.http import HttpResponse, JsonResponse
from django.urls import path
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from .backends import get_backend
from . import jobs
from . import models


def job_info(job):
    return {
        'id': job.id,
        'state': job.state,
    }


def home(request):
    return JsonResponse({
        'version': '0.0.1',
    })


def upload_source(request):
    upload = models.Upload.objects.create(data=request.body)
    return JsonResponse({'id': upload.pk})


def create_job(request):
    spec = json.loads(request.body or '{}')

    sources = []
    for source in spec.get('sources', {}):
        assert isinstance(source['name'], str)
        upload = models.Upload.objects.get(pk=source['id'])
        sources.append((source['name'], upload))

    job = jobs.create(get_backend(), sources)
    return JsonResponse(job_info(job))


def get_job(request, pk):
    job = get_object_or_404(models.Job, pk=pk)

    jobs.poll(job)
    return JsonResponse(job_info(job))


def kill_job(request, pk):
    job = get_object_or_404(models.Job, pk=pk)
    jobs.kill(job)
    return JsonResponse({'ok': True})


def download_artifact(request, pk, name):
    job = get_object_or_404(models.Job, pk=pk)
    data = job.artifact_set.get(name=name).data
    return HttpResponse(data)


def route(**views):
    @csrf_exempt
    @require_http_methods(list(views))
    def view(request, **kwargs):
        return views[request.method](request, **kwargs)

    return view


urls = [
    path('', route(GET=home)),
    path('jobs', route(POST=create_job)),
    path('jobs/source', route(PUT=upload_source)),
    path('jobs/<int:pk>', route(GET=get_job, DELETE=kill_job)),
    path('jobs/<int:pk>/artifacts/<path:name>', route(GET=download_artifact)),
]
