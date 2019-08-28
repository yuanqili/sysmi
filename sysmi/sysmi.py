import datetime
import os
import time

import psutil
from termcolor import colored


class CPUStat:

    def __init__(self):
        pass

    @staticmethod
    def cpu_count():
        return psutil.cpu_count()

    @staticmethod
    def info():
        virtual_memory = psutil.virtual_memory()
        swap_memory = psutil.swap_memory()
        net_io_counters = psutil.net_io_counters()

        return {
            'cpu_count': psutil.cpu_count(),
            'cpu_percent': psutil.cpu_percent(),
            'per_cpu_percent': psutil.cpu_percent(percpu=True),
            'virtual_memory': {
                'used': virtual_memory.used,
                'total': virtual_memory.total,
            },
            'swap_memory': {
                'percent': swap_memory.percent,
            },
            'net_io_counters': {
                'bytes_sent': net_io_counters.bytes_sent,
                'bytes_recv': net_io_counters.bytes_recv,
            },
            'boot_time': psutil.boot_time(),
            'ts': time.time(),
        }


class MonitorBoard:

    def __init__(self, host, length=3600, cpu_count=8):
        self.hostname = host

        self.total_cpu_percent = [0] * length
        self.per_cpu_percents = []
        self.cpu_count = cpu_count
        for _ in range(cpu_count):
            self.per_cpu_percents.append([0] * length)
        self.memory_used = [0] * length
        self.swap_memory = [0] * length
        self.bytes_sent = [0] * length
        self.bytes_recv = [0] * length
        self.boot_time = [0] * length

        self.last_updated = [datetime.datetime.utcnow()]

    def add(self, info):
        self.last_updated.append(datetime.datetime.utcnow())
        self.total_cpu_percent.append(info['cpu_percent'])
        for percent, cpu_history in zip(info['per_cpu_percent'], self.per_cpu_percents):
            cpu_history.append(percent)
        self.memory_used.append(info['virtual_memory']['used'] / info['virtual_memory']['total'] * 100)
        self.swap_memory.append(info['swap_memory']['percent'])
        self.bytes_sent.append(info['net_io_counters']['bytes_sent'])
        self.bytes_recv.append(info['net_io_counters']['bytes_recv'])
        self.boot_time.append(info['boot_time'])

    def print(self, percpu=True, length=None):
        if length is None:
            _, cols = os.popen('stty size', 'r').read().split()
            length = int(cols) - 12

        if (datetime.datetime.utcnow() - self.last_updated[-1]).seconds >= 2:
            print(colored('●', color='red'), self.hostname)
        else:
            print(colored('●', color='green'), self.hostname)

        print(f'CPU {self.plot(self.total_cpu_percent[-length:])} {self.total_cpu_percent[-1]:6.2f}%')
        if percpu:
            for cpu_history, i, in zip(self.per_cpu_percents, list(range(self.cpu_count))):
                print(f' {i:02d} {self.plot(cpu_history[-length:])} {cpu_history[-1]:6.2f}%')
        print(f'MEM {self.plot(self.memory_used[-length:])} {self.memory_used[-1]:6.2f}%')
        print(f'SWP {self.plot(self.swap_memory[-length:])} {self.swap_memory[-1]:6.2f}%')

        bytes_out = self.readable_size(self.bytes_sent[-1] - self.bytes_sent[-2])
        bytes_in = self.readable_size(self.bytes_recv[-1] - self.bytes_recv[-2])
        net_str = f'NET ↑ {bytes_out} ↓ {bytes_in}'
        uptime = self.seconds_to_dhms(int(time.time() - self.boot_time[-1]))
        up_str = f'uptime {uptime}'
        print(f'{net_str}{" " * (length + 12 - len(net_str) - len(up_str))}{up_str}')

    @staticmethod
    def plot(x, chars=u'▁▂▃▄▅▆▆▇▇██', sep=''):
        return sep.join([chars[int(j) // 10] for j in x])

    @staticmethod
    def readable_size(size, decimal_places=2):
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                break
            size /= 1024.0
        return f'{size:.{decimal_places}f}{unit}/s'

    @staticmethod
    def seconds_to_dhms(secs):
        seconds_to_minute = 60
        seconds_to_hour = 60 * seconds_to_minute
        seconds_to_day = 24 * seconds_to_hour
        days = secs // seconds_to_day
        secs %= seconds_to_day
        hours = secs // seconds_to_hour
        secs %= seconds_to_hour
        minutes = secs // seconds_to_minute
        secs %= seconds_to_minute
        seconds = secs
        return f'{days} days, {hours:02d}:{minutes:02d}:{seconds:02d}'
