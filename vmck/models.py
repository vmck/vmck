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

    def __str__(self):
        return f"{self.id} ({self.state})"
