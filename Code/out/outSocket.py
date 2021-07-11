#!/usr/bin/env python3
import socket,os,sys,traceback
from time import sleep

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
        # if 'sysStat' in data.decode('utf-8'):
        if 'sysStat' in incoming:
            sysList = ['outBgFan.service','outCam.service','outMainDATA.service','outWPBoot.service','rainMainDATA.service']
            result = []
            sysStat = []
            listLen = str(len(sysList))
            conn.sendall(str.encode(listLen))
            for item in sysList:
                status = os.system('systemctl is-active --quiet ' + item)
                if status == 0:
                    strStat = 'OK - '
                else:
                    strStat = 'NOT OK - '
                conn.sendall(str.encode(strStat))
                conn.sendall(str.encode(item + ':'))
            pass
#
        # if 'stat' in data.decode('utf-8'):
        if 'stat' in incoming:
            sysList = ['outBgFan.service','outCam.service','outMainDATA.service','outWPBoot.service','rainMainDATA.service']
            result = []
            sysStat = []
            listLen = str(len(sysList))
            for item in sysList:
                status = os.system('systemctl is-active --quiet ' + item)
                if status == 0:
                    strStat = 'OK'
                else:
                    strStat = 'NOT OK'
                resp = '{:>14s} {:<22s}'.format(strStat + " :", item)
                conn.sendall(str.encode(resp + '\n'))
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
        authActions = ["sysStat","stat","quit"]
        if not any(x in incoming for x in authActions):
            inc = incoming.rstrip()
            outText = ('Sorry, but ' + inc + ' is not in my list of authorized actions.\n')
            try:
                conn.sendall(str.encode(outText))
                pass
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

