from django.db import models


class Job(models.Model):
    STATE_NEW = 'new'
    STATE_RUNNING = 'running'
    STATE_DONE = 'done'

    STATE_CHOICES = [
        (STATE_NEW, 'New'),
        (STATE_RUNNING, 'Running'),
        (STATE_DONE, 'Done'),
    ]

    state = models.CharField(
        max_length=32,
        choices=STATE_CHOICES,
        default=STATE_NEW,
    )

    name = models.CharField(max_length=1024, default='default')
    token = models.CharField(max_length=128, default='none')

    def __str__(self):
        return f"{self.id} ({self.state})"
