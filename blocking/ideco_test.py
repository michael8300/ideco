import requests
import json
requests.packages.urllib3.disable_warnings()


class Ideco:
    def __init__(self, ip = '', port = '8443', user = '', password = '', rest_path = '/'):
        self.ip = ip
        self.port = port
        self.user = user
        self.password = password
        self.rest_path = rest_path

        self.base_url = f'https://{ip}:{port}'
        self.session = requests.Session()
        self.session.verify = False
        self.logged = False

    def __enter__(self):
        self.login()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logout()


    def get_from_endpoint(self, url):
        try:
            response = self.session.get(url = url)
            response.raise_for_status()
            return self.parse_json(response)
        except requests.exceptions.HTTPError as e:
            print(f"HTTP error occurred: {e}")
            return None
    
    def post_to_endpoint(self, url, obj_dict):
        try:
            response = self.session.post(url = url, json = obj_dict)
            response.raise_for_status()
            return response
        except requests.exceptions.HTTPError as e:
            print(f"HTTP error occurred: {e}")
            return None

    def put_to_endpoint(self, url, obj_dict):
        try:
            response = self.session.put(url = url, json = obj_dict)
            response.raise_for_status()
            return response
        except requests.exceptions.HTTPError as e:
            print(f"HTTP error occurred: {e}")
            return None

    def parse_json(self, response):
        try:
            response = response.json()
            return response
        except:
            print('Ошибка парсинга JSON')


    def login(self):
        url = f'{self.base_url}/web/auth/login'
        data = {
            "login": self.user,
            "password": self.password,
            "rest_path": self.rest_path
        }
        response = self.post_to_endpoint(url, data)
        if response is not None:
            print("Успешная авторизация")
            self.logged = True
        else:
            raise RuntimeError("Ошибка авторизации")

    def logout(self):
        if self.logged:
            url = f'{self.base_url}/web/auth/login'
            response = self.session.delete(url)
            if response.status_code == 200:
                self.logged = False
                print("Выход выполнен")
            response.raise_for_status()
        exit()


    def get_users_list(self):
        url = f'{self.base_url}/user_backend/users'
        return self.get_from_endpoint(url)

    def get_rules_list(self):
        url = f'{self.base_url}/firewall/rules/forward'
        return self.get_from_endpoint(url)

    def get_ip_address_lists(self):
        url = f'{self.base_url}/aliases/ip_address_lists'
        return self.get_from_endpoint(url)

    def block_user(self, username):
        block_rule = self.find_rule_for_block()
        user_id = self.find_user(username)
        block_rule['source_addresses'].append(f"user.id.{user_id}")
        url = f'{self.base_url}/firewall/rules/forward/{block_rule.pop("id")}'
        data = block_rule
        response = self.put_to_endpoint(url, data)
        if response is not None:
            print(f'Пользователь {username} заблокирован')
        else:
            print(f'Не удалось заблокировать пользователя {username}')

    def unblock_user(self, username):
        block_rule = self.find_rule_for_block()
        user_id = self.find_user(username)
        block_rule['source_addresses'].remove(f"user.id.{user_id}")
        url = f'{self.base_url}/firewall/rules/forward/{block_rule.pop("id")}'
        data = block_rule
        response = self.put_to_endpoint(url, data)
        if response is not None:
            print(f'Пользователь {username} разблокирован')
        else:
            print(f'Не удалось разблокировать пользователя {username}')

    def block_ip(self, address):
        blocklist_id, data = self.find_blocklist()
        data['values'].append(address)
        data.pop('type', None)
        url = f'{self.base_url}/aliases/ip_address_lists/{blocklist_id}'
        response = self.put_to_endpoint(url, data)
        if response is not None:
            print(f'Адрес {address} заблокирован')
        else:
            print(f'Не удалось заблокировать адрес {address}')

    def unblock_ip(self, address):
        blocklist_id, data = self.find_blocklist()
        data['values'].remove(address)
        data.pop('type', None)
        url = f'{self.base_url}/aliases/ip_address_lists/{blocklist_id}'
        response = self.put_to_endpoint(url, data)
        if response is not None:
            print(f'Адрес {address} разблокирован')
        else:
            print(f'Не удалось разблокировать адрес {address}')


    def find_rule_for_block(self):
        for rule in self.get_rules_list():
            if rule["id"] == 500:
                return(rule)
        print("Блокирующее правило не найдено")
        return self.logout()

    def find_user(self, username):
        for user in self.get_users_list():
            if user["login"] == username:
                return(user["id"])
        print("Пользователь не найден")
        return self.logout()

    def find_blocklist(self):
        for list in self.get_ip_address_lists().items():
            if list[1]["title"] == 'List_for_test_api':
                return list
        print("Список для блокировки не найден")
        return self.logout()



with Ideco(ip='', port='8443', user='', password='') as api_client:
    # print(api_client.block_user(''))
    print(api_client.block_ip(''))

