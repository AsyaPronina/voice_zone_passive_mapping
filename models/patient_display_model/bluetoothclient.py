# -*- coding: utf-8 -*-
"""
Created on Tue Sep  7 14:34:43 2021

@author: AlexVosk
"""

import time
import json
from io import BytesIO
from datetime import datetime

import numpy as np
from tqdm import tqdm

import bluetooth
import javaobj

# datetime object containing current date and time
now = datetime.now()

#print("now =", now)

# dd/mm/YY H:M:S
#dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
#print("date and time =", dt_string)

class BluetoothServer:
    uuid = "04c6093b-0000-1000-8000-00805f9b34fb"
    addr = None
    name = 'BluetoothServer'

    def __init__(self):
        super(BluetoothServer).__init__()
        self.server_socket = None
        self.client_socket = None
        self.marshaller = None

    def connect(self):
        self.server_socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        self.server_socket.bind(("", bluetooth.PORT_ANY))
        bluetooth.advertise_service(self.server_socket, self.name, service_id = self.uuid,
                                    service_classes = [self.uuid, bluetooth.SERIAL_PORT_CLASS],
                                    profiles = [bluetooth.SERIAL_PORT_PROFILE])
        print('wait for connection')
        self.server_socket.listen(1)
        self.client_socket, client_info = self.server_socket.accept()
        print('Bluetooth connection esteblished')
        
        self.marshaller = javaobj.JavaObjectMarshaller()
        self.marshaller.references = []
        self.marshaller.object_stream = BytesIO()
        self.marshaller._writeStreamHeader()
        print('Marshaller created')

    def _create_message(self, mtype, subtype, file_number, tone):
        file_name = "{}.jpg".format(file_number)
        if subtype == 'other':
            file_name = '0' + file_name
        message = {"type":mtype,"subtype":subtype,"fileName":file_name,"tone":tone}
        return message

    def send_message(self, mtype, subtype, file_number, tone):
        message = self._create_message(mtype, subtype, file_number, tone)
        data_json = json.dumps(message)
        self.marshaller.write_string(data_json)
        data_java = self.marshaller.object_stream.getvalue()
        self.marshaller.object_stream = BytesIO()
        self.client_socket.send(data_java)

    def show_pictures(self, nblocks, npictures, random, t_blank, t_picture, sound_picture):
        order = []
        while len(order) < nblocks:
            block_order = np.copy(self.object_order[:npictures])
            if random:
                np.random.shuffle(block_order)
            else:
                block_order = np.sort(block_order)
            if len(order) != 0:
                if block_order[0] == order[-1][-1]:
                    continue
            order.append(block_order)
        order = np.concatenate(order).astype(np.int32)
        print(order)
        print('show {} pictures'.format(order.shape[0]))

        now = datetime.now()
        order_filename = now.strftime("%d%m%Y%H%M%S") + '.txt'
        np.savetxt(order_filename, order, fmt='%i')

        time.sleep(5)
        self.send_message(mtype="show_image", subtype='other', file_number=2, tone=False)
        time.sleep(t_picture)
        for i in order:
            t1 = time.perf_counter()
            self.send_message(mtype="show_image", subtype='other', file_number=0, tone=sound_picture)
            #t2 = time.perf_counter()
            time.sleep(t_blank)
            #t3 = time.perf_counter()
            #for _ in range(int(t_picture/t_blank)):
            self.send_message(mtype="show_image", subtype='object', file_number=i, tone=False)
            #t4 = time.perf_counter()
            time.sleep(t_picture)
            t4 = time.perf_counter()
            print(t4-t1)

        self.send_message(mtype="show_image", subtype='other', file_number=3, tone=False)
        time.sleep(t_picture)
        self.send_message(mtype="show_image", subtype='other', file_number=0, tone=False)
        time.sleep(t_picture)


    def show_actions(self, nblocks, npictures, random, t_blank, t_picture, sound_picture):
        order = []
        while len(order) < nblocks:
            block_order = np.copy(self.object_order[:npictures])
            if random:
                np.random.shuffle(block_order)
            else:
                block_order = np.sort(block_order)
            if len(order) != 0:
                if block_order[0] == order[-1][-1]:
                    continue
            order.append(block_order)
        order = np.concatenate(order).astype(np.int32)
        print(order)
        print('show {} pictures'.format(order.shape[0]))
        
        now = datetime.now()
        order_filename = now.strftime("%d%m%Y%H%M%S") + '.txt'
        np.savetxt(order_filename, order, fmt='%i')
        
        time.sleep(t_picture)
        self.send_message(mtype="show_image", subtype='other', file_number=1, tone=False)
        time.sleep(t_picture)
        for i in tqdm(order):
            #t1 = time.perf_counter()
            self.send_message(mtype="show_image", subtype='other', file_number=0, tone=sound_picture)
            #t2 = time.perf_counter()
            time.sleep(t_blank)
            #t3 = time.perf_counter()
            self.send_message(mtype="show_image", subtype='action', file_number=i, tone=False)
            #t4 = time.perf_counter()
            time.sleep(t_picture)
            #print(t4-t3, t2-t1)
        self.send_message(mtype="show_image", subtype='other', file_number=3, tone=False)
        time.sleep(t_picture)
        self.send_message(mtype="show_image", subtype='other', file_number=0, tone=False)
        time.sleep(t_picture)


    def close(self):
        self.marshaller.object_stream.close()
        try:
            self.client_socket.close()
        except AttributeError as e:
            # in case if no client is connected
            pass


if __name__ == '__main__':
    bluetooth_server = BluetoothServer()
    bluetooth_server.connect()
    bluetooth_server.show_objects(nblocks=1, npictures=50, random=False, t_blank=0.7, t_picture=3, sound_picture=True)
    #bluetooth_server.show_actions(nblocks=1, npictures=50, random=False, t_blank=0.7, t_picture=3, sound_picture=True)
    bluetooth_server.close()
    
    
    
    