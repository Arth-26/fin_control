import random

from faker import Faker
from locust import HttpUser, between, task

fake = Faker('pt_BR')

usuarios = [
    {'username': 'example1@gmail.com', 'password': '123456'},
    {'username': 'example2@gmail.com', 'password': '123456'},
    {'username': 'example3@gmail.com', 'password': '123456'},
    {'username': 'example4@gmail.com', 'password': '123456'},
    {'username': 'example5@gmail.com', 'password': '123456'},
    {'username': 'example6@gmail.com', 'password': '123456'},
    {'username': 'example7@gmail.com', 'password': '123456'},
    {'username': 'example8@gmail.com', 'password': '123456'},
    {'username': 'example9@gmail.com', 'password': '123456'},
    {'username': 'example10@gmail.com', 'password': '123456'},
]


class ApiUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):

        usuario = random.choice(usuarios)
        response = self.client.post('/auth/login', data={'username': usuario['username'], 'password': usuario['password']})
        data = response.json()

        token = data['access_token']

        self.headers = {'Authorization': f'Bearer {token}'}

    @task(2)
    def get_users(self):
        self.client.get('/users', headers=self.headers)

    @task
    def get_user_per_id(self):
        id = random.randint(1, 10)
        self.client.get(f'/users/{id}')
