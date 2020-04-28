# -*- coding: utf-8 -*-
"""
Created on Mon Apr  6 14:38:53 2020

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
# HEADERSIZE = 5#int(input('Enter the header size: ',))
# BUFFERSIZE = 10#int(input('Enter the buffer size(in bytes): '))
# SENTENCELENGTH = 8#int(input('Enter sentence length to transfer: ',))
# NPACKETS = 50#int(input('Enter the size of a packet: ',))

HEADERSIZE = int(input('Enter the header size: ',))
BUFFERSIZE = int(input('Enter the buffer size(in bytes): '))
SENTENCELENGTH = int(input('Enter sentence length to transfer: ',))
NPACKETS = int(input('Enter the size of a packet: ',))

s.bind((IP,PORT))
s.listen()

clientsocket, address = s.accept()
print("Connection from:",address)

def send_packet(websocket, msg_list, header_len, n_packets):
    s_t = time.time()
    bytes_sent = 0
    for i in range(n_packets):
        msg = f'{len(msg_list[i]):<{header_len}}' + msg_list[i]
        # print(msg)
        bytes_sent += websocket.send(bytes(msg,'utf-8'))
        websocket.recv(1)

    time_taken = time.time() - s_t
    return bytes_sent, time_taken

def receive_packet(websocket, buffer_size, header_len, n_packets):
    s_t = time.time()
    recv_msg_list = []
    data_recvd = 0
    for i in range(n_packets):
        full_msg = ''
        msg_not_recieved = True
        while msg_not_recieved:
            msg = websocket.recv(buffer_size) # 8 bytes is the buffer size, keep it atleast equal to headersize
            if full_msg == '':
                msglen = int(msg[:header_len].strip())
                data_recvd += msglen + buffer_size

            full_msg += msg.decode('utf-8')

            msglen_recvd = len(full_msg)-header_len

            if msglen_recvd == msglen:
                print('-------------------Full msg recvd---------------------')
                msg_recvd = full_msg[header_len:]
                recv_msg_list.append(msg_recvd)
                print('Received message:',msg_recvd)
                print('---------------------xxxxxxxxxxxxxxxxxxxxxxxxxxxx------------------------')
                websocket.send(bytes('1','utf-8'))
                msg_not_recieved = False
    time_taken = time.time()-s_t
    return data_recvd, time_taken, recv_msg_list


msg_list = [make_sentence(s_words,SENTENCELENGTH) for x in range(NPACKETS)]

amt_sent,t_s = send_packet(clientsocket, msg_list,HEADERSIZE,NPACKETS)

amt_recvd,t_r,recv_msg = receive_packet(clientsocket,BUFFERSIZE,HEADERSIZE,NPACKETS)
