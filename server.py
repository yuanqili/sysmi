import json
import os
import socket
import time
from multiprocessing import Process, Queue

from dotenv import load_dotenv

from sysmi.sysmi import MonitorBoard

if __name__ == '__main__':

    load_dotenv()

    server_host = '0.0.0.0'
    server_port = int(os.getenv('server_port'))
    server_address = ('0.0.0.0', server_port)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(server_address)

    monitors = {}
    q = Queue()

    def recv(_q):
        while True:
            size, address = sock.recvfrom(4)
            size = int.from_bytes(size, 'little')

            message, address = sock.recvfrom(size)
            h, _ = address
            message = message.decode('utf-8')
            i = json.loads(message)

            _q.put((h, i))


    pp = Process(target=recv, args=(q, ))
    pp.start()

    print('\033c', end='')
    while True:
        print('\033[1;1H')
        while not q.empty():
            item = q.get()
            host, info = item
            if host not in monitors:
                hostname = socket.gethostbyaddr(host)[0]
                monitors[host] = MonitorBoard(host=f'{hostname} ({host})', cpu_count=info['cpu_count'])
            monitors[host].add(info)

        for host in monitors:
            monitors[host].print(percpu=True)
            print()

        time.sleep(1)
