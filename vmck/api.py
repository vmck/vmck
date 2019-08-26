import json

from django.conf import settings
from django.http import JsonResponse
from django.urls import path
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from .backends import get_backend, get_submission
from .nomad import launch, job
from .jobs import nomad_id
from .models import Job
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


def create_submission(request):
    options = json.loads(request.body) if request.body else {}  # TODO validate

    jobs = Job.objects.create()
    jobs.state = jobs.STATE_RUNNING

    submission_id = nomad_id(jobs)
    options['vm']['cpu_mhz'] = int(options['vm']['cpus']) * settings.QEMU_CPU_MHZ  # noqa: E501

    launch(
        job(
            id=submission_id,
            name='submission-test',
            taskgroups=[get_submission().task_group(jobs, options)]
            )
        )

    jobs.save()

    return JsonResponse({'id': submission_id})


def create_job(request):
    options = json.loads(request.body) if request.body else {}  # TODO validate

    options.setdefault('cpus', 1)
    options.setdefault('memory', 512)
    options.setdefault('image_path', 'imgbuild-master.qcow2.tar.gz')
    options['name'] = options.get('name') or 'default'
    options['cpu_mhz'] = options['cpus'] * settings.QEMU_CPU_MHZ

    job = jobs.create(get_backend(), options)

    return JsonResponse(job_info(job))


def get_job(request, pk):
    job = get_object_or_404(models.Job, pk=pk)

    ssh_remote = jobs.poll(job)
    rv = dict(job_info(job), ssh=ssh_remote)
    return JsonResponse(rv)


def kill_job(request, pk):
    job = get_object_or_404(models.Job, pk=pk)
    jobs.kill(job)
    return JsonResponse({'ok': True})


def route(**views):
    @csrf_exempt
    @require_http_methods(list(views))
    def view(request, **kwargs):
        return views[request.method](request, **kwargs)

    return view


urls = [
    path('', route(GET=home)),
    path('jobs', route(POST=create_job)),
    path('jobs/<int:pk>', route(GET=get_job, DELETE=kill_job)),
    path('submission', route(POST=create_submission)),
]
