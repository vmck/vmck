from django.http import JsonResponse
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


@require_http_methods(['POST'])
def jobs_(request):
    job = jobs.create(get_backend())
    return JsonResponse(job_info(job))


@require_http_methods(['GET', 'DELETE'])
def job_(request, pk):
    job = get_object_or_404(models.Job, pk=pk)

    if request.method == 'GET':
        jobs.poll(job)
        return JsonResponse(job_info(job))

    if request.method == 'DELETE':
        jobs.kill(job)
        jobs.poll(job)
        return JsonResponse(job_info(job))


urls = [
    path('', home),
    path('jobs', jobs_),
    path('jobs/<int:pk>', job_),
]
