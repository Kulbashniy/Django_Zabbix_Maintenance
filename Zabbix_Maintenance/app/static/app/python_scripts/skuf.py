import requests
import json

class Skuf():

    password = 'xxxxxxxxxx'
    login = 'xxxxxxxx'
    login_url = 'https://skuf-portal.gosuslugi.ru/login'
    session = None


    @classmethod
    def log_in(cls):
        # Авторизуемся на сайте и получаем сессию
        cls.session = requests.Session()
        cls.session.get('https://skuf-portal.gosuslugi.ru/rest/user/')
        data = {
            'password': cls.password,
            'resetSession': False,
            'timezone': 'Europe/Moscow',
            'username': cls.login
            }
        cls.session.post(cls.login_url, json=data)


    @classmethod
    def request_crq_time(cls, crq):
        # @param crq - string 'CRQXXXXXXXXXXXX'
        # @rtype dict - {'error' : {....}, 'content': {'start_time': time, 'end_time': time}}
        # content in @rtype - optional (if error.code==0)
        search_crq_url = 'https://skuf-portal.gosuslugi.ru/rest/change/details'
        data = {
            'id': crq
            }
        data = cls.session.post(search_crq_url, json=data)
        response_json = data.json()
        if response_json.get('error').get('code') == 0:
            plan = response_json.get('content').get('change').get('result').get('Plan')
            end = plan.get('Scheduled End Date')
            start = plan.get('Scheduled Start Date')
            return {'error': response_json.get('error'), 'content': {'start_time': start, 'end_time': end}}
        else:
            return {'error': response_json.get('error')}


    @classmethod
    def get_crq_time(cls, crq):
        # @param crq - string 'CRQXXXXXXXXXXXX'
        # @rtype dict - {'error' : {....}, 'content': {'start_time': time, 'end_time': time}}
        # content in @rtype - optional (if error.code==0)
        if cls.session == None:
            cls.log_in()
        try:
            return cls.request_crq_time(crq)
        except:
            cls.log_in()    # try log_in again
            return cls.request_crq_time(crq)


