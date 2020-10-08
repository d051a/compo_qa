import requests
import re
import datetime
import paramiko


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
        except Exception as e:
            print(e)

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
        except:
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
        except:
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
        except:
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
        except:
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

    def get_net_compilation_percent(self, ndigits=2) -> float: # ОКРУГЛЕНИЕ !!!!!!
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

    # @staticmethod
    # def get_time_delta(current_time, start_time, output_format) -> str:
    #     time_delta = current_time - start_time
    #     d = {"days": time_delta.days}
    #     d["hours"], rem = divmod(time_delta.seconds, 3600)
    #     d["minutes"], d["seconds"] = divmod(rem, 60)
    #     return output_format.format(**d)

    @staticmethod
    def get_time_delta(current_time, start_time, output_format) -> str:
        def correct_num_format(num):
            return num if num > 9 else '0' + str(num)
        time_delta = current_time - start_time
        days = time_delta.days
        hours = rem = divmod(time_delta.seconds, 3600)
        d = {"days": correct_num_format(days)}
        d["hours"], rem = correct_num_format(hours)
        d["minutes"], d["seconds"] = correct_num_format(divmod(rem, 60))
        return output_format.format(**d)

    @staticmethod
    def get_ssh_connection(ip_address: str, username: str, password: str, port: str, connect_try=5) -> paramiko.SSHClient:
        i = 1
        while True:
            try:
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                # ssh.load_host_keys(os.path.expanduser(os.path.join("~", ".ssh", "known_hosts")))
                ssh.connect(hostname=ip_address, username=username, password=password, port=int(port))
                return ssh
            except paramiko.AuthenticationException:
                print('ERROR : Authentication failed because of irrelevant details!')
            except:
                print(f'Could not SSH to {ip_address}, waiting for it to start')
                return None

    @staticmethod
    def sftp_transfer_file(ssh: paramiko.SSHClient, localpath_to_file: str, remotepath_to_file: str) -> int:
        try:
            sftp = ssh.open_sftp()
            sftp.put(localpath_to_file, remotepath_to_file)
            sftp.close()
            ssh.close()
            return 0
        except:
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
        except:
            print(f'Не удалось выполнить команду на удаленном устройства {ip_address}')
            return None

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
        except:
            print(f'Что-то пошло не так. Файлы не скопированы!')
            return 1

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


def main():
    # statistic = ChaosStatisctic(ip='172.16.26.96')
    # utils = Utils()
    # start_time = utils.get_time_now()
    # time.sleep(1)
    # current_time = utils.get_time_now()
    # elapsed_time = utils.get_time_delta(current_time, start_time, "{hours}:{minutes}:{seconds}")
    # print(f'DRAWED: {statistic.get_drawed_images_percent()} drawed: {statistic.images_succeeded} {elapsed_time}')
    # print(f'NETLOG: {elapsed_time}: {statistic.online_esl} {statistic.get_net_compilation_percent()}%')
    pass


if __name__ == "__main__":
    main()
