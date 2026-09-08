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


if __name__ == '__main__':
    auth_headers = {}
    login_status, login_body = request('/api/v1/login', method='POST', data={'email':'audit@example.com','password':'secret123'})
    if login_status == 200:
        token = login_body['access_token']
        auth_headers['Authorization'] = f'Bearer {token}'

    print('SUBJECTS_LIST', request('/api/v1/subjects', headers=auth_headers))
    print('SUBJECTS_CREATE', request('/api/v1/subjects', method='POST', data={'subject_name':'Math','class_name':'10','board':'CBSE'}, headers=auth_headers))
    print('UNITS_CREATE', request('/api/v1/units', method='POST', data={'subject_id':1,'unit_name':'Algebra'}, headers=auth_headers))
    print('BLOOMS_CREATE', request('/api/v1/bloom-levels', method='POST', data={'level_name':'Remember'}, headers=auth_headers))
    print('QUESTIONS_CREATE', request('/api/v1/questions', method='POST', data={'subject_id':1,'unit_id':1,'bloom_level_id':1,'question_text':'What is 2+2?','marks':2,'difficulty':'easy'}, headers=auth_headers))
    print('GENERATE_PAPER', request('/api/v1/generate-paper', method='POST', data={'board':'CBSE','class_name':'10','subject_id':1,'units':[1],'total_marks':2,'bloom_distribution':{'Remember':100}}, headers=auth_headers))
    print('PROTECTED_NO_TOKEN', request('/api/v1/subjects', method='GET'))
