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

checks = [
    ('duplicate_register', request('/api/v1/register', method='POST', data={'name':'Audit','email':'audit@example.com','password':'secret123','role':'teacher'})),
    ('bad_login', request('/api/v1/login', method='POST', data={'email':'audit@example.com','password':'wrong'})),
    ('invalid_question_marks', request('/api/v1/questions', method='POST', data={'subject_id':1,'unit_id':1,'bloom_level_id':1,'question_text':'bad','marks':0,'difficulty':'easy'}, headers=auth_headers)),
    ('invalid_unit_subject', request('/api/v1/units', method='POST', data={'subject_id':999,'unit_name':'Bad'}, headers=auth_headers)),
    ('missing_subject_detail', request('/api/v1/subjects/999', headers=auth_headers)),
    ('unauth_subjects_list', request('/api/v1/subjects')),
]

for name, result in checks:
    print(name, result)
