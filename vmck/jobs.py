from time import time
from . import nomad
from . import vms


def create():
    job_id = str(int(time()))

    nomad.launch(
        nomad.job(
            id=job_id,
            name=f"vmck {job_id}",
            taskgroups=[vms.task_group()],
        ),
    )

    return job_id
