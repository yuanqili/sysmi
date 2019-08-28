import json
import os
import socket
import time

from dotenv import load_dotenv

from sysmi import CPUStat

if __name__ == '__main__':

    load_dotenv()
    stat = CPUStat()

    server_ip = os.getenv('server_ip')
    server_port = int(os.getenv('server_port'))
    server_address = (server_ip, server_port)
    print(f'server address: {server_address}')

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    while True:
        message = bytes(json.dumps(stat.info()), 'utf-8')
        length = (len(message)).to_bytes(4, 'little')

        sock.sendto(length, server_address)
        sock.sendto(message, server_address)
        time.sleep(1)
