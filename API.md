# VMCK API

All API calls require authentication, TBD.

## Methods

### `GET /v0/`
Returns general information about the service.

Reponse:
```json
{
  "version": "0.0.1"
}
```

### `PUT /v0/jobs/source`
Upload source file for a future job. Returns a new ID.

Request body should be the source file.

Reponse:
```json
{"id": "$source_id", "size": 1337}
```

### `POST /v0/jobs`
Creates a new job.

Request:
```json
{
  "evaluator": {
    "driver": "qemu",
    "image": "https://repository.grid.pub.ro/cs/so/linux-2019/so-ubuntu-18-04.ova",
    "command": ["bash", "hello.sh"]
  },
  "sources": [
    {"name": "hello.sh", "id": "$source_id"}
  ],
  "meta": {
    "any": "random data"
  }
}
```

Response:
```json
{
  "id": "$job_id",
  "status": "queued",
  "meta": {
    "any": "random data"
  }
}
```

### `GET /v0/job/:id`
Returns the job identified by `:id`.

Reponse:
```json
{
  "id": "$job_id",
  "status": "queued|running|success|failure",
  "meta": {
    "any": "random data"
  },
  "events": [
    {"message": "Job started", "time": "$iso_timestamp"}
  ],
  "output": "...step1...\n...step2...\n...step3...\n",
  "artifacts": [
    {"name": "grade.vmr", "size": 1337}
  ]
}
```

### `GET /v0/job/:id/artifacts/:name`
Downloads artifact identified by `:name` from job `:id`.
