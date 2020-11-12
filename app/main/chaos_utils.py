import requests
import re
import datetime
import paramiko
import json
import time
from paramiko.ssh_exception import SSHException
from requests.adapters import HTTPAdapter


DEFAULT_TIMEOUT = 5 # seconds


class TimeoutHTTPAdapter(HTTPAdapter):
    def __init__(self, *args, **kwargs):
        self.timeout = DEFAULT_TIMEOUT
        if "timeout" in kwargs:
            self.timeout = kwargs["timeout"]
            del kwargs["timeout"]
        super().__init__(*args, **kwargs)

    def send(self, request, **kwargs):
        timeout = kwargs.get("timeout")
        if timeout is None:
            kwargs["timeout"] = self.timeout
        try:
            result = super().send(request, **kwargs)
            return result
        except requests.exceptions.ConnectTimeout:
            print('Превышено число попыток подключения к хосту')
            return None


class ChaosConnector:
    def __init__(self, ip='127.0.0.1', port=19872, url=''):
        self.ip_address = ip
        self.port = port
        self.url = url
        self.response = self.__request()

    def __request(self):
        try:
            request = requests.get(
                f"http://{self.ip_address}:{self.port}/{self.url}", timeout=3)
            response = request.text
            return response
        except requests.exceptions.ConnectionError:
            print(f'Cannot connect to {self.ip_address}')
            return None
        except Exception as e:
            print(e)
            return None

    def __str__(self):
        return str(self.response)


class ChaosStatisctic:
    def __init__(self, ip='127.0.0.1', port=19872, url='get_statistics'):
        self.ip = ip
        self.port = port
        self.url = url
        self.text = self.__get_response

    def __str__(self):
        return self.text

    @property
    def __get_response(self):
        response = ChaosConnector(ip=self.ip, port=self.port, url=self.url)
        return str(response)

    def __get_stat_attr(self, re_pattern):
        try:
            result = re.search(re_pattern, self.text)
            return result.group(1)
        except Exception as error:
            print(f'__get_stat_attr method error: {error}')
            return ''

    @property
    def total_nodes(self) -> int:
        result = self.__get_stat_attr(r'Total nodes: (\d+)')
        if result == '':
            return 0
        else:
            return int(result)

    @property
    def inaccessible_nodes(self) -> int:
        result = self.__get_stat_attr(r'Inaccessible nodes: (\d+)')
        if result == '':
            return 0
        else:
            return int(result)

    @property
    def total_number_routes(self) -> int:
        result = self.__get_stat_attr(r'Total number of routes: (\d+)')
        if result == '':
            return 0
        else:
            return int(result)

    @property
    def maximum_route_length(self) -> int:
        result = self.__get_stat_attr(r'Maximum route length: (\d+)')
        if result == '':
            return 0
        else:
            return int(result)

    @property
    def average_route_length(self) -> float:
        result = self.__get_stat_attr(r'Average route length: (\d+\.\d+)')
        if result == '':
            return 0
        else:
            return float(result)

    @property
    def accessible_nodes_percent(self) -> float:
        result = self.__get_stat_attr(r'Accessible nodes \(%\): (\d+\.\d+)')
        if result == '':
            return 0
        else:
            return float(result)

    @property
    def elapsed_time(self) -> float:
        result = self.__get_stat_attr(r'Elapsed time: (\d+\.\d+)')
        if result == '':
            return 0
        else:
            return float(result)

    @property
    def total_esl(self) -> int:
        result = self.__get_stat_attr(r'Total ESLs: (\d+)')
        if result == '':
            return 0
        else:
            return int(result)

    @property
    def online_esl(self) -> int:
        result = self.__get_stat_attr(r'Online ESLs: (\d+)')
        if result == '':
            return 0
        else:
            return int(result)

    @property
    def images_in_transit(self) -> int:
        result = self.__get_stat_attr(r'Images in transit: (\d+)')
        if result == '':
            return 0
        else:
            return int(result)

    @property
    def images_in_draw(self) -> int:
        result = self.__get_stat_attr(r'Images in draw: (\d+)')
        if result == '':
            return 0
        else:
            return int(result)

    @property
    def images_in_draw_queue(self) -> list:
        queue_string = self.__get_stat_attr(r'Images in draw: \d+ \((.*)\)')
        try:
            queue = [int(queue) for queue in queue_string.split(', ')]
            return queue
        except Exception as error:
            print(f'images_in_draw_queue function error: {error}')
            return []

    @property
    def images_in_resend_queue(self) -> int:
        result = self.__get_stat_attr(r'Images in resend queue: (\d+)')
        if result == '':
            return 0
        else:
            return int(result)

    @property
    def images_succeeded(self) -> int:
        result = self.__get_stat_attr(r'Images succeeded: (\d+)')
        if result == '':
            return 0
        else:
            return int(result)

    @property
    def images_failed(self) -> int:
        result = self.__get_stat_attr(r'Images failed: (\d+)')
        if result == '':
            return 0
        else:
            return int(result)

    @property
    def currently_scanning(self) -> int:
        result = self.__get_stat_attr(r'Currently scanning: (\d+)')
        if result == '':
            return 0
        else:
            return int(result)

    @property
    def network_mode(self) -> str:
        return self.__get_stat_attr(r'Network mode: (.*)')

    @property
    def network_mode_percent(self) -> int:
        if self.network_mode == 'Complete':
            return 100
        if self.network_mode == 'Free Hunt':
            return 66
        if self.network_mode == 'Fast Build':
            return 33
        else:
            return 0

    @property
    def connects(self) -> int:
        result = self.__get_stat_attr(r'Connects: (\d+)')
        if result == '':
            return 0
        else:
            return int(result)

    @property
    def nodes_routes(self) -> dict:
        """
        Возвращает словарь нод и количества их маршрутов

        :rtype: dict
        :return: словарь нод и количество их маршрутов: {'нода': маршрут}

        """
        first_substring = '--------NODES: --------'
        last_substring = '------- LOAD: ---------'
        start_parse_point = self.text.find(first_substring)+len(first_substring)
        end_parse_point = self.text.find(last_substring)
        nodes = self.text[start_parse_point:end_parse_point]
        nodes_routes = {}
        try:
            for node in nodes.split('\n\t')[1:-1]:
                node, routes_num = node.split(': ')
                nodes_routes[node] = int(routes_num)
            return nodes_routes
        except Exception as error:
            print(f'nodes_routes function error: {error}')
            return {}

    @property
    def nodes_num(self):
        nodes_num = len(self.nodes_routes.keys())
        return nodes_num

    def get_node_routes_num(self, node_mac: str) -> str:
        """
        Вовращает число маршрутов для отдельной ноды по ее мак-адресу.

        :param node_mac: мак-адрес ноды
        :type node_mac: str
        :rtype str
        :return: число маршрутов для отдельной ноды
        """
        try:
            node_route = self.nodes_routes[node_mac]
            return node_route
        except KeyError:
            return ''

    @property
    def nodes_load(self) -> dict:
        """
        Возвращает словарь нод и их загруженности (load)

        :rtype: dict
        :return: словарь нод и количество их загруженности: {'нода': load}

        """
        substring = '------- LOAD: ---------'
        start_parse_point = self.text.find(substring) + len(substring)
        nodes = self.text[start_parse_point:]
        nodes_load = {}
        try:
            for node in nodes.split('\n\t')[1:]:
                node, node_load = node.split(': ')
                nodes_load[node] = float(node_load[:-2])
            return nodes_load
        except Exception as error:
            print(f'nodes_load function error: {error}')
            return {}

    def get_node_load_percent(self, node_mac) -> str:
        """
        Вовращает процент загрузки ноды по ее мак адресу

        :param node_mac: мак-адрес ноды
        :type node_mac: str
        :rtype str
        :return: процент загрузки для отдельной ноды
        """
        try:
            node_load = self.nodes_load[node_mac]
            return node_load
        except KeyError:
            return ''

    def get_drawed_images_percent(self, ndigits=2) -> float:
        """
        Возвращает процент отрисованных ценников.

        :param ndigits: количество знаков после запятой
        :type ndigits: int
        :rtype: float
        :return: процент отрисованных ценников
        """
        try:
            drawed_percent = float((float(self.images_succeeded) / float(self.total_esl)) * float(100))
            drawed_percent = f"{drawed_percent:.{ndigits}f}"
            return float(drawed_percent)
        except ZeroDivisionError:
            return float(0)

    def get_net_compilation_percent(self, ndigits=2) -> float:
        """
        Возвращает процент компиляции сети
        :param ndigits: количество знаков после запятой
        :type ndigits: int
        :rtype: float
        :return: процент компиляции сети
        """
        try:
            get_net_compilation_percent = float((float(self.online_esl) / float(self.total_esl)) * float(100))
            get_net_compilation_percent = f"{get_net_compilation_percent:.{ndigits}f}"
            return float(get_net_compilation_percent)
        except ZeroDivisionError:
            return float(0)

    def get_true_net_compilation_percent(self) -> float:
        """
        Возвращает правильный процент сборки сети
        :rtype: float
        :return: процент компиляции сети
        """
        try:
            total_nodes = self.total_nodes
            inaccessible_nodes = self.inaccessible_nodes
            nodes_num = self.nodes_num
            net_compilation_percent = ((total_nodes - inaccessible_nodes - nodes_num) / (total_nodes - nodes_num)) * 100
            return float(net_compilation_percent)
        except ZeroDivisionError:
            return float(0)


class Utils:
    @staticmethod
    def get_time_now() -> datetime.datetime:
        """Возвращает текущее время"""
        return datetime.datetime.now()

    @staticmethod
    def get_time_delta(current_time, start_time, output_format) -> str:
        def correct_num_format(num):
            return num if num > 9 else '0' + str(num)
        time_delta = current_time - start_time
        rem = divmod(time_delta.seconds, 3600)[1]
        hours = divmod(time_delta.seconds, 3600)[0]
        minutes = divmod(rem, 60)[0]
        seconds = divmod(rem, 60)[1]
        times = {'days': time_delta.days,
                 'hours': correct_num_format(hours),
                 'minutes': correct_num_format(minutes),
                 'seconds': correct_num_format(seconds)
                 }
        return output_format.format(**times)

    @staticmethod
    def get_ssh_connection(ip_address: str, username: str, password: str, port: str, connect_try=3)\
            -> paramiko.SSHClient:
        try_num = 0
        while try_num < connect_try:
            try:
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(hostname=ip_address, username=username, password=password, port=int(port))
                return ssh
            except paramiko.AuthenticationException:
                print('ERROR : Authentication failed because of irrelevant details!')
                try_num = connect_try
            except paramiko.ssh_exception.SSHException as error:
                print(f'Error: {error}')
                try_num += 1
            except (SSHException, OSError) as error:
                print(f'Could not SSH to {ip_address}, waiting for it to start. Error: {error}')
                time.sleep(2)
                try_num += 1

    @staticmethod
    def sftp_transfer_file(ssh: paramiko.SSHClient, localpath_to_file: str, remotepath_to_file: str) -> int:
        try:
            sftp = ssh.open_sftp()
            sftp.put(localpath_to_file, remotepath_to_file)
            sftp.close()
            ssh.close()
            return 0
        except Exception as error:
            print('sftp_transfer_file function error: ', error)
            return 1

    @staticmethod
    def run_remote_command(ip_address: str,
                           user_name: str,
                           password: str,
                           port: str,
                           command: str) -> tuple:
        ssh_connection = Utils.get_ssh_connection(ip_address, user_name, password, port)
        try:
            stdin, stdout, stderr = ssh_connection.exec_command(command)
            stdout_result = stdout.readlines()
            stdout_result = "".join(stdout_result)
            stdout_error = stderr.readlines()
            stdout_error = "".join(stdout_error)
            return stdout_result, stdout_error
        except Exception as error:
            print(f'Не удалось выполнить команду на удаленном устройства {ip_address} error: {error}')

    @staticmethod
    def run_remote_command_no_wait(ip_address: str,
                                   user_name: str,
                                   password: str,
                                   port: str,
                                   command: str):
        ssh_connection = Utils.get_ssh_connection(ip_address, user_name, password, port)
        ssh_connection.exec_command(command)

    @staticmethod
    def copy_file_over_ssh(ip_address: str,
                           user_name: str,
                           password: str,
                           port: str,
                           localpath_to_file: str,
                           remotepath_to_file: str) -> int:
        try:
            ssh = Utils.get_ssh_connection(ip_address, user_name, password, port)
            Utils.sftp_transfer_file(ssh, localpath_to_file, remotepath_to_file)
            return True
        except Exception as error:
            print(f'Что-то пошло не так. Файлы не скопированы! copy_file_over_ssh function error: {error}')
            return False

    @staticmethod
    def zip_file(files_paths: list) -> str:
        import socket
        from zipfile import ZipFile
        from datetime import datetime
        from os.path import basename
        now = datetime.now()
        date_time = now.strftime("%Y-%m-%d_%H-%M")
        hostname = socket.gethostname()
        archive_name = f'archive_{hostname}_{date_time}.zip'
        with ZipFile(archive_name, 'w') as zip_archive:
            for file_path in files_paths:
                try:
                    zip_archive.write(file_path, basename(file_path))
                except FileNotFoundError:
                    print(f"Файл не был добавлен в архив, так как не был найден по указанному пути: '{file_path}'")
        return archive_name

    @staticmethod
    def run_shell_command(command: str) -> int:
        import os
        run_command = os.system(command)
        return run_command

    @staticmethod
    def remove_file(path_file):
        import os
        try:
            os.remove(path_file)
        except FileNotFoundError:
            print(f"Файл не был удалён, так как не был найден по указанному пути: '{path_file}'")


class ChaosConfigurationInfo:
    def __init__(self, ip='127.0.0.1', ssh_port=22, chaos_port=19872, login='pi', password='CompoM123'):
        self.ip_address = ip
        self.login = login
        self.ssh_port = ssh_port
        self.chaos_port = chaos_port
        self.password = password
        self.list_node_attributes = self.__get_list_node_attributes()
        self.chaos_config = self.__get_chaos_config()

    def __get_list_node_attributes(self):
        try:
            request = requests.get(
                f"http://{self.ip_address}:19872/list_node_attributes", timeout=3)
            response = request.text
            return response
        except requests.exceptions.ConnectionError:
            print(f'Cannot connect to {self.ip_address}')
        except Exception as e:
            print(e)

    def __get_chaos_config(self):
        config_data = Utils.run_remote_command(self.ip_address, self.login, self.password, str(self.ssh_port),
                                               f'cat /var/Componentality/Chaos/chaos_config.json'
                                               )
        if config_data is None:
            return None
        try:
            config_json = json.loads(config_data[0])
        except json.decoder.JSONDecodeError:
            time_now = datetime.datetime.now().strftime("%d.%m.%y %H:%M:%S")
            print(f'{time_now} FAIL: Это не JSON. Что-то пошло не так. Данные не получены...')
            print(f'STDOUT: {config_data[0]}: STDERR: {config_data[1]}')
            return None
        except TypeError:
            return None
        return config_json

    @staticmethod
    def version_hr(ver):
        v_hex = '%08x' % ver
        v = '%02d' % int(v_hex[0:2], 16) + '.%02d' % int(v_hex[2:4], 16) + '.%02d' % int(v_hex[4:6], 16) + '.%02d' % int(v_hex[6:8], 16)
        return v

    @staticmethod
    def check_device_is_dongle(list_esl):
        if not list_esl:
            return True
        else:
            return False

    @staticmethod
    def add_version_data(version_dict, version):
        if version_dict.get(version, None):
            version_dict[version] += 1
        else:
            version_dict[version] = 1

    def default_devices(self):
        chaos_config = self.chaos_config
        if chaos_config == ('', ''):
            return False
        if chaos_config is not None:
            names_ports = chaos_config['DEFAULT_RSERVERS']
            return names_ports

    def get_ips_by_names(self):
        ip_port = {}
        rservers_list = self.default_devices()
        if rservers_list is not None:
            for address in rservers_list:
                host_name, port = address.split(':')
                ip = Utils.run_remote_command(
                    self.ip_address,
                    self.login,
                    self.password,
                    str(self.ssh_port),
                    f'net lookup {host_name}')[0].rstrip()
                if host_name == '127.0.0.1':
                    ip_port[f'{self.ip_address}:{port}'] = ''
                    continue
                ip_port[f'{ip}:{port}'] = ''
            return ip_port

    @property
    def distributing_device_num(self):
        default_rservers = self.default_devices()
        if not default_rservers:
            return 'н/д'
        else:
            distributing_device_num = len(set([rserver.split(':')[0] for rserver in default_rservers]))
            return distributing_device_num

    @property
    def dongles_num(self):
        rq_cnt = 100500
        timeout = 1
        rservers_names_ports = __class__.default_devices(self)
        rservers_ips_ports = __class__.get_ips_by_names(self)
        rserver_dongles_tmp = []
        if rservers_ips_ports is not None:
            for num, server_ip in enumerate(rservers_ips_ports):
                server_ip = 'http://' + server_ip
                try:
                    r = requests.post(server_ip, json={'command': 'list-roots', 'request-id': rq_cnt}, timeout=timeout)
                    rq_cnt += 1
                    roots = json.loads(r.text)["roots"]
                    rserver_name_wo_port = rservers_names_ports[num].split(':')[0]
                    rserver_dongles_tmp.append(f'{rserver_name_wo_port}: {len(roots)} шт.   ')
                except Exception as error:
                    print(f'dongles_num function error: {error}')
                    rserver_name_wo_port = rservers_names_ports[num].split(':')[0]
                    rserver_dongles_tmp.append(f'{rserver_name_wo_port}: n/a')
            rserver_dongles_string = '\n'.join(rserver_dongles_tmp)
            return rserver_dongles_string
        else:
            rserver_dongles_string = 'н/д'
            return rserver_dongles_string

    @property
    def version_sum(self):
        http = requests.Session()
        adapter = TimeoutHTTPAdapter(timeout=1)
        http.mount("https://", adapter)
        http.mount("http://", adapter)
        try:
            response = http.post(f'http://{self.ip_address}/api3/login?login=admin&passwd=CompoM123')
            response_json = json.loads(response.text)
            sum_version = response_json['data']['version']
        except json.decoder.JSONDecodeError:
            # print(f'FAIL: Это не JSON. Что-то пошло не так. Данные не получены... \n RESPONSE: {response.text}')
            return 'н/д'
        except KeyError:
            # print(f"Не удалось получить данные из ответа API по ключу ['data']['version'] \n RESPONSE: {response.text}")
            return 'н/д'
        except Exception as error:
            print(f'version_sum method error {error}')
            return 'н/д'
        return sum_version

    @property
    def release_version(self):
        current_version = Utils.run_remote_command(self.ip_address, self.login, self.password, str(self.ssh_port),
                                                   'cd /var/Componentality/Chaos ; git tag --points-at HEAD')
        if current_version == ('', '') or current_version is None:
            return 'н/д'
        else:
            return str(current_version[0]).rstrip()

    @property
    def tree_floor_num(self):
        chaos_config = self.chaos_config
        if chaos_config is not None:
            floor_num = int(chaos_config['DEFAULT_MAXIMUM_ROUTE_LENGTH']) - 1
            return floor_num
        else:
            floor_num = 'н/д'
            return floor_num

    @property
    def version_esl_firmware(self):
        sw_versions = {}
        hw_versions = {}
        dongles_versions = {}
        node_attributes = self.list_node_attributes
        if node_attributes is None:
            return None
        node_attributes_json_data = json.loads(node_attributes)
        for node in node_attributes_json_data['attr'].keys():
            try:
                sw_version = __class__.version_hr(node_attributes_json_data['attr'][node]['node_status']['sw_version'])
                hw_version = __class__.version_hr(node_attributes_json_data['attr'][node]['node_status']['hw_version'])
                esl_list = node_attributes_json_data['attr'][node]['ESLs']
            except KeyError:
                continue
            if ChaosConfigurationInfo.check_device_is_dongle(esl_list):
                ChaosConfigurationInfo.add_version_data(dongles_versions, hw_version)
            else:
                ChaosConfigurationInfo.add_version_data(sw_versions, sw_version)
                ChaosConfigurationInfo.add_version_data(hw_versions, hw_version)
        firmwares = {'sw_versions': str(sw_versions)[1:-1],
                     'hw_versions': str(hw_versions)[1:-1],
                     'dongles_versions': str(dongles_versions)[1:-1],
                     }
        return firmwares

    @property
    def sw_versions(self):
        if self.version_esl_firmware is not None:
            sw_versions = self.version_esl_firmware['sw_versions']
            return sw_versions
        else:
            sw_versions = 'н/д'
            return sw_versions

    @property
    def hw_versions(self):
        if self.version_esl_firmware is not None:
            hw_versions = self.version_esl_firmware['hw_versions']
            return hw_versions
        else:
            hw_versions = 'н/д'
            return hw_versions

    @property
    def dongles_versions(self):
        if self.version_esl_firmware is not None:
            dongles_versions = self.version_esl_firmware['dongles_versions']
            return dongles_versions
        else:
            dongles_versions = 'н/д'
            return dongles_versions

    def all_params(self):
        result_info = {'distributing_device_num': self.distributing_device_num,
                       'dongles_num': self.dongles_num,
                       'version_sum:': self.version_sum,
                       'chaos_version': self.release_version,
                       'chaos_config': self.chaos_config,
                       'tree_floor_num': self.tree_floor_num,
                       'driver_version': self.release_version,
                       'sw_versions': self.sw_versions,
                       'hw_versions': self.hw_versions,
                       'dongles_versions': self.dongles_versions,
                       }
        print('Количетво РУ, шт', self.distributing_device_num)
        # print('Конфигурация РУ', self.___)
        print('Количество донглов на РУ, шт', self.dongles_num)
        print('Версия СУМ:', self.version_sum)
        print('Версия Хаоса:', self.release_version)
        print('Конфигурация Хаоса:', self.chaos_config)
        print('Число этажей дерева:', self.tree_floor_num)
        print('Версия драйвера:', self.release_version)
        print('Версия прошивки ЭЦ:', self.sw_versions)
        print('HW версия ЭЦ:', self.hw_versions)
        print('HW версия донглов:', self.dongles_versions)
        return result_info

    def __str__(self):
        return str(self.all_params())


class SumAPIManager:
    def __init__(self, ip='127.0.0.1', login='admin', password='CompoM123', secure=True):
        self.ip_address = ip
        self.login = login
        self.password = password
        self.headers = {'Content-Type': 'application/json'}
        self.cookie = ''
        self.session_token = ''
        self.secure = secure
        self.session = self.__get_session()
        self.auth = self.__auth()

    def __auth(self):
        url = self.__get_url('api3/login')
        try:
            result = self.session.post(url, params={'login': self.login, 'passwd': self.password}, verify=False)
            self.session_token = {'data': result.cookies.get('qpstkn')}
        except AttributeError:
            result = None
            self.auth = result
            return result

        if result.status_code == 200:
            return result
        if result.status_code == 502:
            print('response code: 502. Необходимо включить службу storesvc')
            return None
        else:
            return None

    def __sent_get_request(self, url_path):
        url = self.__get_url(url_path)
        if self.auth is None:
            return None
        result = self.session.get(url,
                                  headers=self.headers,
                                  cookies=self.cookie,
                                  verify=False)
        return result

    def __sent_post_request(self, url_path, body):
        url = self.__get_url(url_path)
        if self.auth is None:
            return None
        result = self.session.post(url,
                                   json=body,
                                   headers=self.headers,
                                   cookies=self.cookie,
                                   verify=False)
        return result

    def __sent_delete_request(self, url_path):
        url = self.__get_url(url_path)
        if self.auth is None:
            return None
        result = self.session.put(url,
                                  headers=self.headers,
                                  cookies=self.cookie,
                                  verify=False)
        return result

    def __sent_put_request(self, url_path):
        url = self.__get_url(url_path)
        if self.auth is None:
            return None
        result = self.session.delete(url,
                                     headers=self.headers,
                                     cookies=self.cookie,
                                     verify=False)
        return result

    def __get_url(self, url_path):
        if self.secure:
            protocol = 'https'
        else:
            protocol = 'http'
        url = f'{protocol}://{self.ip_address}/{url_path}'
        return url

    @staticmethod
    def __get_session():
        session = requests.Session()
        adapter = TimeoutHTTPAdapter(timeout=1)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        return session

    def get_esls_list(self,):
        if self.auth is None:
            return []
        url_path = 'api3/esl'
        result = self.__sent_get_request(url_path)
        return json.loads(result.text)['data']

    def get_controllers_list(self,):
        if self.auth is None:
            return []
        url_path = 'api3/controller'
        result = self.__sent_get_request(url_path)
        return json.loads(result.text)['data']

    def __repr__(self):
        if self.auth:
            result = f"Успешная авторизация в API СУМ ({self.ip_address}). " \
                f"status_code: {self.auth.status_code}. api_key: {self.session_token['data']}"
            return result
        else:
            result = f"Не удалось авторизоваться в API СУМ ({self.ip_address})"
            return result


def main():
    chaos_ip = '172.16.25.51'
    # -------------Статистика хаоса----------------
    statistic = ChaosStatisctic(ip=chaos_ip)
    print(f'DRAWED: {statistic.get_drawed_images_percent()} drawed: {statistic.images_succeeded}')
    print(f'NETLOG: {statistic.online_esl} {statistic.get_net_compilation_percent()}%')
    # -------------------Утилиты-------------------
    utils = Utils()
    print('Текущее время: ', utils.get_time_now())
    # -------------Конфигурация хаоса--------------
    chaos_info = ChaosConfigurationInfo(ip=chaos_ip)
    # chaos_info.all_params()
    print('Количетво РУ, шт', chaos_info.distributing_device_num)
    print('dongles_num:', chaos_info.dongles_num)
    print('version_sum:', chaos_info.version_sum)
    print('release_version:', chaos_info.release_version)
    print('chaos_config:', chaos_info.chaos_config)
    print('tree_floor_num:', chaos_info.tree_floor_num)
    print('version_driver:', chaos_info.release_version)
    print('sw_versions:', chaos_info.sw_versions)
    print('hw_versions:', chaos_info.hw_versions)
    print('dongles_versions:', chaos_info.dongles_versions)
    # print(chaos_info.all_params())
    # -------------API СУМ--------------

if __name__ == "__main__":
    main()
