# -*- coding: utf-8 -*-
"""
Created on Wed Apr 29 13:34:07 2020

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
# AF_INET--> IPv4
# SOCK_STREAM --> streaming socket
s.bind((IP,PORT))
s.listen()
clientsocket, address = s.accept()
print("Connection from:",address)


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

def record_and_stream_audio(websocket, CHUNK=4000,SAMPLERATE=8000,seconds_to_wait=2,formatt='int16',
          write_to_wav=True, get_devices=False):
    
    "Output raw data has Linear16 encoding"
    
    p = pyaudio.PyAudio()
    if get_devices:
        for x in range(p.get_device_count()):
            info = p.get_device_info_by_index(x)
            print(info['name'])

    CHANNELS=1
    unpack_format= formatt #'int16'
    if formatt == 'int16':
        FORMAT = pyaudio.paInt16
        THRESHHOLD = 3000
    elif formatt == 'int32':
        FORMAT = pyaudio.paInt32
        THRESHHOLD = 9*10**7
    elif formatt == 'float32':
        FORMAT = pyaudio.paFloat32
        THRESHHOLD = 0.09
    else:
        print('Data format not available, taking float32')
        FORMAT = pyaudio.paFloat32

    stream = p.open(format=FORMAT,channels=CHANNELS,rate=SAMPLERATE,
                    input=True,output=True,frames_per_buffer=CHUNK)

    chunks_per_sec = int(SAMPLERATE/CHUNK)

    k=1
    fig, ax = plt.subplots()
    x = np.arange(CHUNK)
    line, = ax.plot(x,np.random.randn(CHUNK))
    if formatt == 'int16':
        ax.set_ylim([-2**15,(2**15)-1])
    elif formatt == 'int32':
        ax.set_ylim([-2**31,(2**31)-1])
    elif formatt == 'float32':
        ax.set_ylim([-1,1])

    keep_recording = True
    start_recording = False

    while keep_recording:
        tmp_raw = stream.read(CHUNK)
        tmp = np.frombuffer(tmp_raw, unpack_format)
        if tmp.max() > THRESHHOLD:
            start_recording = True
            all_data = tmp
            raw_data = tmp_raw
            print('Recording Starts')
            while start_recording:
                data = stream.read(CHUNK)
                dictt = {'raw_chunk':data, 'format': formatt, 'sr': SAMPLERATE}
                d_s,t_s = send_msg(websocket, dictt, HEADERSIZE)
                raw_data += data

                data_unpacked = np.frombuffer(data, unpack_format)
                line.set_ydata(data_unpacked)
                fig.canvas.draw()
                fig.canvas.flush_events()

                all_data = np.concatenate((all_data,data_unpacked),axis=0)

                k +=1
                if k>seconds_to_wait*chunks_per_sec:
                    idx = seconds_to_wait*chunks_per_sec*CHUNK
                    max_value = all_data[-idx:].max()
                    if max_value<THRESHHOLD:
                        print('Recording Stops')
                        plt.close()
                        start_recording = False
                        keep_recording = False
                        dictt = {'raw_chunk':b'close'}
                        d_s,t_s = send_msg(websocket, dictt, HEADERSIZE)
                        s.close()
        else:
            line.set_ydata(tmp)
            fig.canvas.draw()
            fig.canvas.flush_events()

    if write_to_wav:
        duration = int(len(all_data)/SAMPLERATE)
        name = f'audio_{duration}_{formatt}.wav'
        wavfile.write(name,SAMPLERATE, all_data)
        print(f'file {name} saved to working directory')
        return all_data, raw_data, name
    else:
        return all_data, raw_data


arr, raw_data, nm = record_and_stream_audio(clientsocket)
