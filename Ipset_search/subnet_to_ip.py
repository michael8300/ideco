import ipaddress

# def cidr_to_ip_list(cidr):
#     # Создаем объект сети из строки CIDR
#     network = ipaddress.ip_network(cidr, strict=False)
    
#     # Получаем список всех IP-адресов в сети
#     ip_list = [str(ip) for ip in network.hosts()]
    
#     return ip_list

# # Пример использования
# cidr = '172.22.255.0/24'
# ip_list = cidr_to_ip_list(cidr)

# # Записываем IP-адреса в файл или выводим их построчно
# with open('ip_list.txt', 'w') as f:
#     for ip in ip_list:
#         f.write(f"{ip}\n")


import json

# Чтение JSON из файла
file_path = r''  # Укажите путь к вашему JSON-файлу
with open(file_path, 'r') as file:
    data = json.load(file)

for key, value in data.items():
    for a, b in value.items():
        if "tcp:443" in b:
            print(key)


# Извлечение только верхнеуровневых ключей
top_level_keys = list(data.keys())
for key in top_level_keys:
    print(key)

print(top_level_keys)