#!/usr/bin/env python3

from urllib.request import Request, urlopen, HTTPError
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

    req = Request(
        url,
        body,
        headers,
        method=method,
    )

    with urlopen(req) as res:
        if res.status >= 200 and res.status < 300:
            content = res.read()
            if (res.headers.get('Content-Type') == 'application/json' and
                    len(content)):
                return json.loads(content)
            else:
                return None
        else:
            raise HTTPError(url, res.status, res.msg, res.headers, res)


def main():
    job_vmck = {}
    data = {}

    # nomad hcl->json convertor
    url_parser = 'http://10.66.60.1:4646/v1/jobs/parse'
    # nomad api for job submission
    url_submit = 'http://10.66.60.1:4646/v1/jobs'

    data['Canonicalize'] = True
    data['JobHCL'] = open('vmck.nomad', 'r').read()

    # conversion from hcl->json
    vmck_json = request(method='POST', url=url_parser, data=data)

    # every nomad file that will be submitted must have a 'Job' stanza
    job_vmck['Job'] = vmck_json

    request(method='POST', url=url_submit, data=job_vmck)


if __name__ == '__main__':
    main()
