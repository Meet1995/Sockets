# -*- coding: utf-8 -*-
"""
Created on Wed Apr 29 13:50:21 2020

@author: mg21929
"""

import socket
import time
import os
import pyaudio
import matplotlib.pyplot as plt
import pickle
import numpy as np
from scipy.io import wavfile

IP = '192.168.43.115'
PORT = 1234
HEADERSIZE = 15
BUFFERSIZE = 2000

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((IP,PORT))


def send_msg(websocket, dictt, header_len):
    msg = pickle.dumps(dictt)
    msg = bytes(f'{len(msg):<{header_len}}', 'utf-8') + msg
    s_t = time.time()
    bytes_sent = websocket.send(msg)
    websocket.recv(1)
    time_taken = time.time() - s_t
    return bytes_sent, time_taken

def receive_msg(websocket, buffer_size, header_len):
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
            dictt = pickle.loads(full_msg[header_len:])
            print('*******************Full msg recvd******************')
            msg_not_recieved = False
    return msglen+buffer_size, time_taken, dictt


def receive_streaming_audio(websocket, buffer_size, header_len):
    all_data_raw = b''
    receiving = True
    start_time = True
    while receiving:
        d_r, t_r, dictt = receive_msg(websocket,buffer_size, header_len)
        if dictt['raw_chunk'] != b'close':
            if start_time:
                s_t = time.time()
                start_time = False
            all_data_raw += dictt['raw_chunk']
            sample_rate = dictt['sr']
            formatt = dictt['format']

        else:
            all_data = np.frombuffer(all_data_raw, formatt)
            wavfile.write(f"received_file.wav",sample_rate, all_data)
            print('Audio file saved')
            receiving = False
            time_taken = time.time()-s_t
    return all_data, all_data_raw, sample_rate, formatt, time_taken

all_data, all_data_raw, sample_rate, formatt, t_r = receive_streaming_audio(s, BUFFERSIZE, HEADERSIZE)
