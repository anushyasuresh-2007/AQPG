import json
import urllib.request
from urllib.error import HTTPError, URLError

base = 'http://127.0.0.1:8011'


def request(path, method='GET', data=None, headers=None):
    req = urllib.request.Request(base + path, method=method)
    if headers:
        for k, v in headers.items():
            req.add_header(k, v)
    if data is not None:
        req.data = json.dumps(data).encode('utf-8')
        req.add_header('Content-Type', 'application/json')
    try:
        with urllib.request.urlopen(req) as response:
            body = response.read().decode('utf-8')
            return response.status, json.loads(body) if body else None
    except HTTPError as exc:
        body = exc.read().decode('utf-8')
        try:
            payload = json.loads(body)
        except Exception:
            payload = body
        return exc.code, payload
    except URLError as exc:
        return None, str(exc.reason)


if __name__ == '__main__':
    print('HEALTH', request('/health'))
    print('API_HEALTH', request('/api/v1/health'))
    print('REGISTER', request('/api/v1/register', method='POST', data={'name':'Audit','email':'audit@example.com','password':'secret123','role':'teacher'}))
    print('LOGIN', request('/api/v1/login', method='POST', data={'email':'audit@example.com','password':'secret123'}))
