import json
import random
import string
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


suffix = ''.join(random.choices(string.ascii_lowercase, k=4))
email = f'audit{suffix}@example.com'

status, _ = request('/api/v1/register', method='POST', data={'name':'Audit','email':email,'password':'secret123','role':'teacher'})
login_status, login_body = request('/api/v1/login', method='POST', data={'email':email,'password':'secret123'})
token = login_body['access_token'] if login_status == 200 else ''
auth_headers = {'Authorization': f'Bearer {token}'}

# health
print('health', request('/health'))
print('api_health', request('/api/v1/health'))

# subjects
print('subjects_list', request('/api/v1/subjects'))
print('subjects_create', request('/api/v1/subjects', method='POST', data={'subject_name':'Science','class_name':'10','board':'CBSE'}, headers=auth_headers))
print('subjects_get', request('/api/v1/subjects/1', headers=auth_headers))
print('subjects_update', request('/api/v1/subjects/1', method='PUT', data={'subject_name':'Science Updated'}, headers=auth_headers))

# units
print('units_list', request('/api/v1/units'))
print('units_create', request('/api/v1/units', method='POST', data={'subject_id':1,'unit_name':'Physics'}, headers=auth_headers))
print('units_get', request('/api/v1/units/1', headers=auth_headers))
print('units_update', request('/api/v1/units/1', method='PUT', data={'unit_name':'Physics Updated'}, headers=auth_headers))

# bloom levels
print('blooms_list', request('/api/v1/bloom-levels'))
print('blooms_create', request('/api/v1/bloom-levels', method='POST', data={'level_name':'Apply'}, headers=auth_headers))
print('blooms_get', request('/api/v1/bloom-levels/1', headers=auth_headers))
print('blooms_update', request('/api/v1/bloom-levels/1', method='PUT', data={'level_name':'Apply Updated'}, headers=auth_headers))

# questions
print('questions_list', request('/api/v1/questions'))
print('questions_create', request('/api/v1/questions', method='POST', data={'subject_id':1,'unit_id':1,'bloom_level_id':1,'question_text':'What is force?','marks':3,'difficulty':'medium'}, headers=auth_headers))
print('questions_get', request('/api/v1/questions/1', headers=auth_headers))
print('questions_update', request('/api/v1/questions/1', method='PUT', data={'question_text':'What is acceleration?'}, headers=auth_headers))

# generate paper
print('generate_paper', request('/api/v1/generate-paper', method='POST', data={'board':'CBSE','class_name':'10','subject_id':1,'units':[1],'total_marks':3,'bloom_distribution':{'Apply Updated':100}}, headers=auth_headers))

# delete operations
print('delete_question', request('/api/v1/questions/1', method='DELETE', headers=auth_headers))
print('delete_unit', request('/api/v1/units/1', method='DELETE', headers=auth_headers))
print('delete_bloom', request('/api/v1/bloom-levels/1', method='DELETE', headers=auth_headers))
print('delete_subject', request('/api/v1/subjects/1', method='DELETE', headers=auth_headers))
