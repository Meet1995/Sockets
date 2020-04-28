# -*- coding: utf-8 -*-
"""
Created on Sun Apr  5 17:14:27 2020

@author: mg21929
"""

import socket
import time
import pickle
from scipy.io import wavfile

IP = '192.168.43.115'
PORT = 1234
HEADERSIZE = 15
BUFFERSIZE = 2000

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((IP,PORT))

def send_data(websocket, dictt, header_len):
    msg = pickle.dumps(dictt)
    msg = bytes(f'{len(msg):<{header_len}}', 'utf-8') + msg
    s_t = time.time()
    bytes_sent = websocket.send(msg)
    websocket.recv(1)
    time_taken = time.time() - s_t
    return bytes_sent, time_taken

def receive_data(websocket, buffer_size, header_len):
    full_msg = b''
    msg_not_recieved = True
    s_t = time.time()
    while msg_not_recieved:
        msg = websocket.recv(buffer_size) # 8 bytes is the buffer size, keep it atleast equal to headersize
        if full_msg == b'':
            msglen = int(msg[:header_len].strip())
            print(msglen)

        full_msg += msg

        msglen_recvd = len(full_msg)-header_len

        if msglen_recvd == msglen:
            websocket.send(bytes('1','utf-8'))
            time_taken = time.time()-s_t
            print('-------------------Full msg recvd---------------------')
            dictt = pickle.loads(full_msg[header_len:])
            print('Received array shape:',dictt['arr'].shape)
            print('---------------------xxxxxxxxxxxxxxxxxxxxxxxxxxxx------------------------')
            msg_not_recieved = False
    return msglen+buffer_size, time_taken, dictt

d_r, t_r, dictt = receive_data(s,BUFFERSIZE, HEADERSIZE)

wavfile.write(f"_{dictt['name']}",dictt['sr'], dictt['arr'])
print('Audio file saved')
