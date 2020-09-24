import django
import os
import time
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "conf.settings")
django.setup()
from main.models import MetricReport, Chaos, NetCompilationStat, NetCompileReport
import json
import requests
from chaos.chaos_utils import Utils as utils
from datetime import datetime

# server_ssh_address = '172.16.25.147'
# server_ssh_address = '172.16.25.245'
# server_ssh_address = '172.16.26.96'
server_ssh_address = '172.16.27.169'

ssh_port = '22'
ssh_user_name = 'pi'
ssh_user_password = 'CompoM123'

# sysreturn = os.system('sudo systemctl stop chaos_webcore')
# sysreturn = os.system('sudo systemctl start chaos_webcore')


def reboot_devices():
    def check_host_alive(chaos_ip, slave_ip, slave_port):
        rq_cnt = 100500
        time_out = 3
        url = f'http://{slave_ip}:{slave_port}'
        if chaos_ip == '127.0.0.1':
            url = f'http://{chaos_ip}:{slave_port}'
        try:
            request = requests.post(url, json={'command': 'ping', 'request-id': rq_cnt}, timeout=time_out)
        except:
            print('Driver at %s is not available, no ping' % url)
            return False
        try:
            request = requests.post(url, json={'command': 'list-roots', 'request-id': rq_cnt}, timeout=time_out)
            rq_cnt += 1
            roots = json.loads(request.text)["roots"]
            print("Driver at %s roots: %s" % (url, ', '.join(roots)))
        except:
            print('Driver at %s is not available, no roots' % url)
            return False
        return True

    def get_ips_by_names(name_port_list):
        ip_port = {}
        for address in name_port_list:
            host_name, port = address.split(':')
            ip = utils.run_remote_command(
                server_ssh_address,
                ssh_user_name,
                ssh_user_password,
                ssh_port,
                f'net lookup {host_name}')[0].rstrip()
            if host_name == '127.0.0.1':
                ip_port[f'{server_ssh_address}:{port}'] = ''
                continue
            ip_port[f'{ip}:{port}'] = ''
        return ip_port

    def get_default_servers(server_ssh_address, ssh_user_name, ssh_user_password, ssh_port):
        run_command = utils.run_remote_command(server_ssh_address, ssh_user_name, ssh_user_password, ssh_port,
                                               'cat /var/Componentality/Chaos/chaos_config.json')
        if run_command == ('', ''):
            return None
        chaos_config = json.loads(run_command[0])
        names_ports = chaos_config['DEFAULT_RSERVERS']
        return names_ports

    def check_all_alive(rebooted_servers_ips_ports, max_work_time_minutes=5):
        time_start = datetime.now()
        while rebooted_servers_ips_ports:
            time.sleep(1)
            time_now = datetime.now()
            elapsed_time = (time_now - time_start).total_seconds() / 60
            if elapsed_time > max_work_time_minutes:
                print(
                    f'Устройства перезагружаются дольше чем {max_work_time_minutes} минут. Процесс перезапуска остановлен!')
                break
                return False
            for address in list(rebooted_servers_ips_ports):
                ip, port = address.split(':')
                alive = check_host_alive(server_ssh_address, ip, port)
                if alive:
                    rebooted_servers_ips_ports.pop(address)
        print('Хаос и все слейвы перезапущены! Все живы!')
        return True

    def reboot_servers_list(servers_ips_ports):
        servers_ips = [server.split(':')[0] for server in servers_ips_ports]
        for ip_address in set(servers_ips):
            try:
                run_command = utils.run_remote_command(ip_address, ssh_user_name, ssh_user_password, ssh_port,
                                                       f'echo {ssh_user_password}|sudo -S sudo reboot')
                print(f'Инициация перезагрузки устройства: {ip_address}')
                return True
            except:
                return False

    chaos = {'ip': server_ssh_address, 'login': ssh_user_name, 'password': ssh_user_password, 'ssh_port': ssh_port, 'port': 19872}
    server_names_ports = get_default_servers(chaos['ip'], chaos['login'], chaos['password'], chaos['ssh_port'])
    if server_names_ports is None:
        print(f"Не удалось получить DEFAULT_RSERVERS в устройства {chaos['ip']}")
        return False
    print(server_names_ports)
    servers_ips_ports = get_ips_by_names(server_names_ports)
    print(servers_ips_ports)
    reboot_servers = reboot_servers_list(servers_ips_ports)
    if not reboot_servers:
        print('Все серверы не перезагружены! Что-то пошло не так')
        return False
    print('OK инициирована перезагрузка всех серверов!')
    time.sleep(30)
    check_servers_alive = check_all_alive(servers_ips_ports, 5)
    if not check_servers_alive:
        print('Не все серверы доступны после перезагрузки! Что-то пошло не так')
        return False
    return True


if __name__ == '__main__':
    reboot_devices()
