#!/usr/bin/env python3


from urllib.request import Request, urlopen, HTTPError
import json


def request(method, url, data=None, headers=None):
    """Makes a request against the JSON url
    :param method: the request method
    :param url: the path in the JSON API
    :param data: the request body
    :type data: bytes|str
    """
    req_url = url
    req_headers = dict(headers or {})
    req_body = None

    if data is not None:
        if isinstance(data, bytes):
            req_body = data
        else:
            req_headers['Content-Type'] = 'application/json'
            req_body = json.dumps(data).encode('utf8')

    req = Request(
        req_url,
        req_body,
        req_headers,
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
    """Main function, nothing special
    """
    job_vmck = {}
    data = {}

    # nomad hcl->json convertor
    url_parser = 'http://10.66.60.1:4646/v1/jobs/parse'
    # nomad api for job submission
    url_submit = 'http://10.66.60.1:4646/v1/jobs'

    data['Canonicalize'] = True
    data['JobHCL'] = open("vmck.nomad", "r").read()

    # conversion from hcl->json
    vmck_json = request(method='POST', url=url_parser, data=data, headers=None)

    # every nomad file that will be submitted must have a 'Job' stanza
    job_vmck['Job'] = vmck_json
    job_submit = json.dumps(job_vmck).encode('utf8')

    request(method='POST', url=url_submit, data=job_submit, headers=None)


if __name__ == "__main__":
    main()
