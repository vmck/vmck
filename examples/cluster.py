#!/usr/bin/env python3

from urllib.request import Request, urlopen
from pathlib import Path
import json
import os

NOMAD_URL = os.environ.get("NOMAD_URL", "http://10.66.60.1:4646")


def request(method, url, data=None, headers=None):
    """Make a request against the JSON url
    :param method: the request method
    :param url: the path in the JSON API
    :param data: the request body
    :type data: bytes|str
    """

    headers = dict(headers or {})
    body = None

    if data is not None:
        if isinstance(data, bytes):
            body = data
        else:
            headers["Content-Type"] = "application/json"
            body = json.dumps(data).encode("utf8")

    req = Request(url, body, headers, method=method)

    with urlopen(req) as res:
        if 200 <= res.status < 300:
            if res.headers.get("Content-Type") == "application/json":
                content = res.read()
                return json.loads(content)
            else:
                return None
        else:
            raise RuntimeError(f"POST failed. {url}, {res.status}, {res.msg}")


def main():
    here = Path(__file__).resolve().parents[0]
    with open(here / "vmck.nomad") as f:
        job_hcl = f.read()

    vmck_json = request(
        method="POST",
        url=f"{NOMAD_URL}/v1/jobs/parse",
        data={"Canonicalize": True, "JobHCL": job_hcl},
    )

    request(method="POST", url=f"{NOMAD_URL}/v1/jobs", data={"Job": vmck_json})


if __name__ == "__main__":
    main()
