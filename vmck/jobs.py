import socket
import logging

from django.conf import settings

from vmck.models import Job
from vmck import nomad
from vmck import consul

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)


def nomad_id(job):
    prefix = settings.NOMAD_JOB_PREFIX
    return f"{prefix}{job.id}"


def create(backend, options):
    job = Job.objects.create()
    job.state = job.STATE_RUNNING
    job.name = options["name"]
    job.backend = backend.name

    nomad.launch(
        nomad.job(
            id=nomad_id(job),
            name=f"{settings.NOMAD_DEPLOYMENT_NAME}#{job.id} {job.name}",
            taskgroups=[backend.task_group(job, options)],
        ),
    )

    job.save()

    return job


def test_ssh_signature(host, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(4)
        try:
            log.debug(f"Connecting to {host}:{port}")
            sock.connect((host, port))
            log.debug(f"Successfully connected to {host}:{port}")
            resp = sock.recv(1000)
            log.debug(f"Received {resp}")
            if resp.startswith(b"SSH-"):
                return True
        finally:
            sock.close()
    except Exception as e:
        log.debug(f"Exception: {e}")
        pass

    return False


def ssh_remote(job):
    health = consul.health(job.id)
    if health:
        check = health[0]
        log.debug(f"Healthcheck for {job.id}: {check['Status']}")
        if check["Status"] == "passing":
            if job.backend == "qemu":
                host = check["Output"].split(":")[0].split()[-1]
                port = int(check["Output"].split(":")[1])
                if test_ssh_signature(host, port):
                    return {
                        "host": host,
                        "port": port,
                        "username": settings.SSH_USERNAME,
                    }
            elif job.backend == "raw_qemu":
                service_id = check["ServiceID"]
                service = consul.service(job.id, service_id)[0]
                log.debug(f"Service {service_id} for {job.id}: {service}")
                return {
                    "host": service["ServiceAddress"],
                    "port": service["ServicePort"],
                    "username": settings.SSH_USERNAME,
                }


def poll(job):
    if job.state == job.STATE_DONE:
        log.warning(f"Polling dead job {job!r}")
        return

    status = nomad.status(nomad_id(job))
    log.debug(f"{job.id} status: {status}")

    if status in [None, "pending"]:
        return

    elif status == "running":
        job.state = job.STATE_RUNNING
        job.save()
        return ssh_remote(job)

    elif status in ["complete", "failed"]:
        job.state = job.STATE_DONE
        job.save()

    else:
        raise RuntimeError(f"Unknown status {status!r}")


def kill(job):
    nomad.kill(nomad_id(job))
