import json
from django.http import HttpResponse, JsonResponse
from django.urls import path
from django.views.decorators.http import require_http_methods
from django.shortcuts import get_object_or_404
from .backends import get_backend
from . import jobs
from . import models


def job_info(job):
    return {
        'id': job.id,
        'state': job.state,
    }


@require_http_methods(['GET'])
def home(request):
    return JsonResponse({
        'version': '0.0.1',
    })


@require_http_methods(['PUT'])
def source_(request):
    upload = models.Upload.objects.create(data=request.body)
    return JsonResponse({'id': upload.pk})


@require_http_methods(['POST'])
def jobs_(request):
    spec = json.loads(request.body)

    sources = []
    for source in spec.get('sources', {}):
        assert isinstance(source['name'], str)
        upload = models.Upload.objects.get(pk=source['id'])
        sources.append((source['name'], upload))

    job = jobs.create(get_backend(), sources)
    return JsonResponse(job_info(job))


@require_http_methods(['GET', 'DELETE'])
def job_(request, pk):
    job = get_object_or_404(models.Job, pk=pk)

    if request.method == 'GET':
        jobs.poll(job)
        return JsonResponse(job_info(job))

    if request.method == 'DELETE':
        jobs.kill(job)
        return JsonResponse({'ok': True})


@require_http_methods(['GET'])
def artifact_(request, pk, name):
    job = get_object_or_404(models.Job, pk=pk)
    data = job.artifact_set.get(name=name).data
    return HttpResponse(data)


urls = [
    path('', home),
    path('jobs', jobs_),
    path('jobs/source', source_),
    path('jobs/<int:pk>', job_),
    path('jobs/<int:pk>/artifacts/<path:name>', artifact_),
]
