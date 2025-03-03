import os
import re
import pandas as pd # type: ignore
import json
import time
from concurrent.futures import ProcessPoolExecutor

# Парсинг файла ipset
def parse_ipsets_file(file_path):
    with open(file_path, 'r') as f:
        content = f.read()
    
    name_match = re.search(r'Name:\s*(\S+)', content)
    members_match = re.search(r'Members:\s*([\s\S]*)', content)
    
    if name_match and members_match:
        name = name_match.group(1)
        members = members_match.group(1).strip().splitlines()
        members_result = []
        for member in members:
            if ',' not in member:
                members_result.append(member + ',any')
            else:
                members_result.append(member)
        members = [member.strip() for member in members_result]
        return name, set(members)
    return None, set()



# Преобразование адреса в целочисленное значение
def ip_to_int(ip):
    return int(''.join(['%02x' % int(x) for x in ip.split('.')]), 16)



# Обработка ipset и преобразование его в dataframe
def process_file(file_path, ips_to_check):
    name, members = parse_ipsets_file(file_path)
    if not name:
        return None
    
    dataframe_ipset = (pd.DataFrame([m.split(',') for m in members], columns=['prefix', 'port'])).groupby('prefix')['port'].apply(list).reset_index()
    dataframe_ipset['name'] = name

    def process_ip(ip):
        if '/' in ip:
            return ip.split('/')
        else:
            return [ip, '32']

    dataframe_ipset[['ip', 'prefix_len']] = dataframe_ipset['prefix'].apply(process_ip).tolist()
    dataframe_ipset['int_ip_addr'] = dataframe_ipset['ip'].map(ip_to_int)
    dataframe_ipset['prefix_len'] = dataframe_ipset['prefix_len'].astype(int)
    dataframe_ipset['netmask'] = dataframe_ipset['prefix_len'].map(lambda x: (0xffffffff << (32 - x)) & 0xffffffff)
    return check_ip_in_ipset(dataframe_ipset, ips_to_check, name)



# Проверка вхождения адреса для поиска в ipset
def check_ip_in_ipset(dataframe_ipset, ips_to_check, name):
    final_results = {}
    for ip in ips_to_check:
        int_ip_addr_to_check = ip_to_int(ip)
        match = ((int_ip_addr_to_check & dataframe_ipset['netmask']) == (dataframe_ipset['int_ip_addr'] & dataframe_ipset['netmask']))
        if match.any():
            matches = dataframe_ipset[match][['ip', 'prefix_len', 'port']].set_index('ip')[['prefix_len', 'port']].to_dict('index')
            for ip, data in matches.items():
                ip_with_mask = f"{ip}/{data['prefix_len']}"
                if name not in final_results:
                    final_results[name] = {}
                final_results[name][ip_with_mask] = data['port']
    return final_results



def main():
    start_time = time.time()

    # Путь к каталогу с файлами
    directory_path = r'C:\Users\m.ognev\Documents\JOB\ipsets'
    check_file_path = r'C:\Users\m.ognev\Documents\JOB\Projects\ideco\check_ips.txt'

    # Создание списка путей к ipset'ам
    ipset_paths = [os.path.join(directory_path, filename) for filename in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, filename))]

    # Получение из файла списка адресов для проверки
    with open(check_file_path, 'r') as f:
        ips_to_check = [line.strip() for line in f.readlines()]

    # Поочередная обработка файлов
    # results_list = [process_file(ipset, ips_to_check) for ipset in ipset_paths]

    # Параллельная обработка файлов
    with ProcessPoolExecutor() as executor:
        results_list = list(executor.map(process_file, ipset_paths, [ips_to_check] * len(ipset_paths)))

    # Составление итогового словаря
    final_results = {}
    for result in results_list:
        if result is not None:
            final_results.update(result)

    # Запись результатов в файл
    with open(r'C:\Users\m.ognev\Documents\JOB\Projects\ideco\result.json', 'w') as result_file:
        json.dump(final_results, result_file, indent=4)

    print("--- %s seconds ---" % (time.time() - start_time))

if __name__ == "__main__":
    main()
