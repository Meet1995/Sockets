# -*- coding: utf-8 -*-
"""
Created on Mon Apr  6 16:25:36 2020

@author: mg21929
"""

import socket
import time
import pandas as pd


IP = '192.168.43.115'
PORT = 1234
HEADERSIZE = int(input('Enter the header size: ',))
BUFFERSIZE = int(input('Enter the buffer size(in bytes): '))
SENTENCELENGTH = int(input('Enter sentence length to transfer: ',))
NPACKETS = int(input('Enter the size of a packet: ',))

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((IP,PORT))

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


amt_recvd,t_r,recv_msg = receive_packet(s, BUFFERSIZE,HEADERSIZE,NPACKETS)
print('*************************************************************************************************')
amt_sent,t_s = send_packet(s,recv_msg,HEADERSIZE,NPACKETS)
