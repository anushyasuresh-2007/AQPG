import json
import urllib.request
from urllib.error import HTTPError

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


login_status, login_body = request('/api/v1/login', method='POST', data={'email':'audit@example.com','password':'secret123'})
token = login_body['access_token'] if login_status == 200 else ''
auth_headers = {'Authorization': f'Bearer {token}'}

print('DELETE_BLOOM_WITH_QUESTION', request('/api/v1/bloom-levels/1', method='DELETE', headers=auth_headers))
print('CREATE_SECOND_BLOOM', request('/api/v1/bloom-levels', method='POST', data={'level_name':'Understand'}, headers=auth_headers))
print('DELETE_BLOOM_EMPTY', request('/api/v1/bloom-levels/2', method='DELETE', headers=auth_headers))
