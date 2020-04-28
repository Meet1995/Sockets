# -*- coding: utf-8 -*-
"""
Created on Sun Apr  5 17:14:27 2020

@author: mg21929
"""

import socket
import time
import pandas as pd

IP = '192.168.43.115'
PORT = 1234
HEADERSIZE = 5
BUFFERSIZE = 10
SENTENCELENGTH = int(input('Enter sentence length to transfer: ',))

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((IP,PORT))

def send_msg(websocket, msg, header_len):
    msg = f'{len(msg):<{header_len}}' + msg
    s_t = time.time()
    bytes_sent = websocket.send(bytes(msg,'utf-8'))
    websocket.recv(1)
    time_taken = time.time() - s_t
    return bytes_sent, time_taken

def receive_msg(websocket, buffer_size, header_len):
    full_msg = ''
    msg_not_recieved = True
    s_t = time.time()
    while msg_not_recieved:
        msg = websocket.recv(buffer_size) # 8 bytes is the buffer size, keep it atleast equal to headersize
        if full_msg == '':
            msglen = int(msg[:header_len].strip())

        full_msg += msg.decode('utf-8')

        msglen_recvd = len(full_msg)-header_len

        if msglen_recvd == msglen:
            websocket.send(bytes('1','utf-8'))
            time_taken = time.time()-s_t
            print('-------------------Full msg recvd---------------------')
            msg_recvd = full_msg[header_len:]
            print('Received message:',msg_recvd)
            print('---------------------xxxxxxxxxxxxxxxxxxxxxxxxxxxx------------------------')
            msg_not_recieved = False
    return msglen+buffer_size, time_taken, msg_recvd

sent_time = []
sent_data = []
recv_time = []
recv_data = []
for i in range(50):
    amt_r,t_r,msg_rcv = receive_msg(s,BUFFERSIZE,HEADERSIZE)
    recv_time.append(t_r)
    recv_data.append(amt_r)

    amt_s,t_s = send_msg(s,msg_rcv,HEADERSIZE)
    sent_time.append(t_s)
    sent_data.append(amt_s)

data_dct = {'sentence_len':[SENTENCELENGTH]*len(recv_time), 'time_taken_to_receive':recv_time, 'data_size_received':recv_data,'time_taken_to_send':sent_time,'data_size_sent':sent_data}

df_client = pd.DataFrame.from_dict(data_dct)
