#!/usr/bin/env python3
## THIS IS THE SOCKET SERVER - IT LISTENS.
##
import socket
import os
import sys
import traceback
from time import sleep
import pickle
import logging

oSockHome = os.path.abspath(os.path.dirname(__file__))
logger = logging.getLogger(__name__)
## Set up logging
#
logging.basicConfig(
    filename=oSockHome + "/outsock.log",
    format="%(asctime)s - %(message)s",
    datefmt="%a, %d %b %Y %H:%M:%S",
    level=logging.INFO,
)

host = ''
port = 64444
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

try:
    s.bind((host, port))
except socket.error as e:
    print(str(e))

while True:
    s.listen(1)
    print('Waiting for a connection.')
    conn, addr = s.accept()
    print('connected to: '+addr[0]+':'+str(addr[1]))
    conn.send(str.encode('Welcome. Use "quit" to close connection.\n'))

    while True:
        data = conn.recv(2048)
        try:
            incoming = data.decode('utf-8')
        except Exception:
            traceback.print_exc(file=sys.stdout)
            incoming = 'An error was caught and displayed.'
            data = str.encode('Nothing good came our way.')
            conn.sendall(data)
            pass
        # print(incoming)
#
        # if 'busted' in data.decode('utf-8'):
        if 'busted' in incoming:
            with open("Busted.pkl", "wb") as bpkl:
                while True:
                    bytes_read = conn.recv(4096)
                    if not bytes_read:
                        break
                    bpkl.write(bytes_read)
            logger.info("Received Busted.pkl")
            with open('Busted.pkl', 'rb') as tpmR:
                bustedstuff = pickle.load(tpmR)
            logger.info(bustedstuff)
            changes = []
            for x in bustedstuff:
                if "off" in bustedstuff[x]:
                    changes.append(bustedstuff[x])
            with open("allbustedstuff.txt", "w") as abs:
                for c in changes:
                    abs.write(c + "\n")
            logger.info("allbustedstuff.txt modified.")
            pass
#
        # if 'quit' in data.decode('utf-8'):
        if 'quit' in incoming:
            conn.send(str.encode('I heard that "quit", man.\n'))
            sleep(1)
            try:
                conn.shutdown(1)
                conn.close()
                print('Connection closed.')
                break
            except Exception:
                traceback.print_exc(file=sys.stdout)
                incoming = 'An error was caught and displayed.'
                pass
# 
        if not data:
            break
#

    conn.close()
else:
    print('All Finished.')
    pass

