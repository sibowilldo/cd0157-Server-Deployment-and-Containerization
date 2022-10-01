'''
Tests for jwt flask app.
'''
import os
import json
import pytest

import main

SECRET = 'TestSecret'
TOKEN = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE1NjEzMDY3OTAsIm5iZiI6MTU2MDA5NzE5MCwiZW1haWwiOiJ3b2xmQHRoZWRvb3IuY29tIn0.IpM4VMnqIgOoQeJxUbLT-cRcAjK41jronkVrqRLFmmk'
EMAIL = 'wolf@thedoor.com'
PASSWORD = 'huff-puff'


@pytest.fixture
def client():
    os.environ['JWT_SECRET'] = SECRET
    main.APP.config['TESTING'] = True
    client = main.APP.test_client()

    yield client


def test_health(client):
    response = client.get('/')
    assert response.status_code == 200
    assert response.json == 'Healthy'


def test_auth(client):
    body = {'email': EMAIL,
            'password': PASSWORD}
    response = client.post('/auth',
                           data=json.dumps(body),
                           content_type='application/json')

    assert response.status_code == 200
    token = response.json['token']
    assert token is not None


def test_auth_returns_400_if_email_is_not_provided(client):
    body = {'password': PASSWORD}
    response = client.post('/auth',
                           data=json.dumps(body),
                           content_type='application/json')

    assert response.status_code == 400
    message = response.json['message']
    assert message == 'Missing parameter: email'


def test_auth_returns_400_if_password_is_not_provided(client):
    body = {'email': EMAIL}
    response = client.post('/auth',
                           data=json.dumps(body),
                           content_type='application/json')

    assert response.status_code == 400
    message = response.json['message']
    assert message == 'Missing parameter: password'


def test_contents_returns_200_if_user_is_authorized(client):
    token = main._get_jwt({'email': EMAIL}).decode('utf-8')
    headers = {'Authorization': f'Bearer {token}'}
    response = client.get('/contents', headers=headers)
    email = response.json['email']
    assert response.status_code == 200
    assert email == EMAIL


def test_contents_returns_401_if_authorization_header_is_not_present(client):
    response = client.get('/contents')
    assert response.status_code == 401


def test_contents_returns_401_if_bearer_token_is_not_valid(client):
    headers = {'Authorization ': 'Bearer Token is Invalid'}
    response = client.get('/contents', headers=headers)
    assert response.status_code == 401

