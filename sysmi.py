import json
import os
import socket

import psutil
from dotenv import load_dotenv


class CPUStat:

    def __init__(self):
        pass

    @staticmethod
    def cpu_count():
        return psutil.cpu_count()

    @staticmethod
    def info():
        return {
            'cpu_count': psutil.cpu_count(),
            'cpu_percent': psutil.cpu_percent(),
            'per_cpu_percent': psutil.cpu_percent(percpu=True),
            'virtual_memory': psutil.virtual_memory(),
            'net_io_counters': psutil.net_io_counters(),
            'swap_memory': psutil.swap_memory(),
            'boot_time': psutil.boot_time(),
        }


if __name__ == '__main__':

    load_dotenv()
    stat = CPUStat()

    server_address = (os.getenv('server_ip'), int(os.getenv('server_port')))
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    while True:
        message = json.dumps(stat.info())
        sock.sendto(message, server_address)
