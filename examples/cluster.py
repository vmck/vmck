#!/usr/bin/env python3

from urllib.request import Request, urlopen
import json


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
            headers['Content-Type'] = 'application/json'
            body = json.dumps(data).encode('utf8')

    req = Request(url, body, headers, method=method)

    with urlopen(req) as res:
        if 200 <= res.status < 300:
            if (res.headers.get('Content-Type') == 'application/json'):
                content = res.read()
                return json.loads(content)
            else:
                return None
        else:
            raise RuntimeError(f'POST failed. {url}, {res.status}, {res.msg}')


def main():
    # nomad hcl->json convertor
    url_parser = 'http://10.66.60.1:4646/v1/jobs/parse'
    # nomad api for job submission
    url_submit = 'http://10.66.60.1:4646/v1/jobs'

    with open('vmck.nomad') as f:
        job_hcl = f.read()

    data = {
        'Canonicalize': True,
        'JobHCL': job_hcl
    }

    # conversion from hcl->json
    vmck_json = request(method='POST', url=url_parser, data=data)

    # every nomad file that will be submitted must have a 'Job' stanza
    request(method='POST', url=url_submit, data={'Job': vmck_json})


if __name__ == '__main__':
    main()
