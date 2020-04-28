# -*- coding: utf-8 -*-
"""
Created on Sun Apr  5 16:17:33 2020

@author: mg21929
"""

import socket
import time
import random
import pandas as pd

s = 'By default in Python 3, we are on the left side in the world of Unicode code points for strings. We only need to go back and forth with bytes while writing or reading the data. Default encoding during this conversion is UTF-8, but other encodings can also be used. We need to know what encoder was used during the decoding process, otherwise we might get errors or get gibberish. A good practice is to decode your bytes in UTF-8 (or an encoder that was used to create those bytes) as soon as they are loaded from a file. Run your processing on unicode code points through your Python code, and then write back into bytes into a file using UTF-8 encoder in the end. This is called Unicode Sandwich'

s_words = s.split()

def make_sentence(s_words, n):
    a = ''
    for x in random.sample(s_words,n):
        if a =='':
            a = a + x
        else:
            a = a + ' ' + x
    return a

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# AF_INET--> IPv4
# SOCK_STREAM --> streaming socket

IP = '192.168.43.115'
PORT = 1234
HEADERSIZE = 5
BUFFERSIZE = 10
SENTENCELENGTH = int(input('Enter sentence length to transfer: ',))

s.bind((IP,PORT))
s.listen()

clientsocket, address = s.accept()
print("Connection from:",address)

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

    msg = make_sentence(s_words,SENTENCELENGTH)

    amt_s,t_s = send_msg(clientsocket,msg,HEADERSIZE)
    sent_time.append(t_s)
    sent_data.append(amt_s)

    amt_r,t_r,msg_rcv = receive_msg(clientsocket,BUFFERSIZE,HEADERSIZE)
    recv_time.append(t_r)
    recv_data.append(amt_r)

data_dct = {'sentence_len':[SENTENCELENGTH]*len(recv_time), 'time_taken_to_receive':recv_time, 'data_size_received':recv_data,'time_taken_to_send':sent_time,'data_size_sent':sent_data}

df_server = pd.DataFrame.from_dict(data_dct)
