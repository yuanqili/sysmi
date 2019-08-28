import time
import os
import psutil


def plot(x, chars=u'▁▂▃▄▅▆▇████', sep=''):
    return sep.join([chars[int(j)//10] for j in x])


def readable_size(size, decimal_places=2):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            break
        size /= 1024.0
    return f'{size:.{decimal_places}f}{unit}/s'


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


class CPUStat:

    def __init__(self):
        pass

    @staticmethod
    def cpu_count():
        return psutil.cpu_count()

    @staticmethod
    def info():
        return {
            'cpu_percent': psutil.cpu_percent(),
            'per_cpu_percent': psutil.cpu_percent(percpu=True),
            'virtual_memory': psutil.virtual_memory(),
            'net_io_counters': psutil.net_io_counters(),
            'swap_memory': psutil.swap_memory(),
            'boot_time': psutil.boot_time(),
        }


if __name__ == '__main__':

    _, columns = os.popen('stty size', 'r').read().split()
    history_len = int(columns) - 12

    stat = CPUStat()
    cpu_count = stat.cpu_count()

    # total cpu history
    total_cpu_percent = [0] * history_len
    # per cpu history
    per_cpu_percents = []
    for _ in range(cpu_count):
        per_cpu_percents.append([0] * history_len)
    # memory used history
    memory_used = [0] * history_len
    # swap memory history
    swap_memory = [0] * history_len
    # last network io
    net_io = psutil.net_io_counters()
    bytes_sent, bytes_recv = net_io.bytes_sent, net_io.bytes_recv

    while True:
        time.sleep(1)
        info = stat.info()

        # total cpu percent
        total_cpu_percent.pop(0)
        total_cpu_percent.append(info['cpu_percent'])
        print(f'CPU {plot(total_cpu_percent)} {total_cpu_percent[-1]:6.2f}%')

        # per cpu percent
        for percent, cpu_history, i, in zip(info['per_cpu_percent'], per_cpu_percents, list(range(cpu_count))):
            cpu_history.pop(0)
            cpu_history.append(percent)
            print(f' {i:02d} {plot(cpu_history)} {cpu_history[-1]:6.2f}%')

        # memory used percent
        memory_used.pop(0)
        memory_used.append(info['virtual_memory'].used / info['virtual_memory'].total * 100)
        print(f'MEM {plot(memory_used)} {memory_used[-1]:6.2f}%')

        # swap memory percent
        swap_memory.pop(0)
        swap_memory.append(info['swap_memory'].percent)
        print(f'SWP {plot(swap_memory)} {swap_memory[-1]:6.2f}%')

        # network io
        net_io = info['net_io_counters']
        bytes_out = readable_size(net_io.bytes_sent - bytes_sent)
        bytes_in = readable_size(net_io.bytes_recv - bytes_recv)
        bytes_sent, bytes_recv = net_io.bytes_sent, net_io.bytes_recv
        uptime = seconds_to_dhms(int(time.time() - info['boot_time']))

        net_str = f'NET ↑ {bytes_out} ↓ {bytes_in}'
        up_str = f'uptime {uptime}'

        print(f'{net_str}{" " * (int(columns) - len(net_str) - len(up_str))}{up_str}')
