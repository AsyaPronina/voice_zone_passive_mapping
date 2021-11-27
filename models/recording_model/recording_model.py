# -*- coding: utf-8 -*-
"""
Created on Sat Feb 29 13:31:28 2020

@author: Alex Vosk
"""

from pylsl import StreamInlet, resolve_stream
import numpy as np
import time
from queue import Queue
from pathlib import Path
import h5py
from threading import Thread


#  qs['input_queue'] no need? Because we are management host and can decide on state on our own?
class RecordingModel:
    def __init__(self, tool_config, qs = None):
        
        # initialize basic tool_configuration
        self.tool_config = tool_config
        self.input_queue = Queue()
        self.output_queue = Queue()
        
        self.cache_size = 4096*4
        self.srate = 4096
        # variables, changed by commands form q
        # FROM COMMANDS FROM DOCTOR VIEW
        
        # inlet_state:
        # 0 - recording disabled
        # 1 - recording enabled
        self.inlet_state = 1
        
        # patient states:
        # -1 - none (not recording)
        # 0 - rest
        # 1 - objects
        # 2 - actions
        self.patient_state = -1
        self.patient_state_old = -1
        
        # picture state:
        # 0 - none
        # 1 - start
        # 2 - stop
        self.picture_state = 0
        
        self.pause = 0
        #self.patient_state_paused = -1
        
        # initialize memort variables
        self.cache = np.zeros((self.cache_size, 73))
        self.memory = [[], [], []]
        self.picture_indices = [[], [], []]
        
        # 
        self.picture_pause = 0
        self.picture_end = 0
        self.index_picture_start = (-1, -1)
        self.index_picture_stop = (-1, -1)
        self.index_pause = (-1, -1)        
        
        self.stream_name = self.tool_config.Recorder.LSLStreamName

        self.thread = Thread(target=self.record, args=())
        self.thread.daemon = True

    def get_input_queue(self):
        return self.input_queue

    def get_output_queue(self):
        return self.output_queue

    def connect(self):
        # Resolve lsl stream
        streams = resolve_stream('name', self.stream_name)
        self._printm('Resolving stream \'{}\', {} streams found'.format(self.stream_name, len(streams)))
        self.inlet = StreamInlet(streams[0], self.srate)
        self._printm('Stream resolved')

    def start(self):
        self.thread.start()

    def record(self):
        #self._printm('Start recording, if \'Recording...\' progress bar is not filling, check lsl input stream')
        self._resolve_q()
        
        channel_sample = 69
        channel_timestemp = 70
        channel_patient_state = 71
        channel_picture_pause = 72
        channel_picture_state = 73
        dataset_width = self.tool_config.Recorder.DatasetWidth

        #with Bar('Recording...', max=1000) as bar:
        cache_index = 0
        while self.inlet_state:
            if not self.inlet_state:
                print('stop')
        #while time.time()-start_time<10:
            self._resolve_q()
            sample, timestamp = self.inlet.pull_sample()

            # if patient state is "-1" - skip
            if self.patient_state == -1:
                continue
            elif self.pause:
                self.picture_pause = 1
                continue

            #if (self.patient_state_old != self.patient_state and cache_index > 0) or (cache_index >= 500):
            if cache_index >= self.cache_size:
                if self.patient_state_old == -1:
                    self.patient_state_old = self.patient_state
                self.output_queue.put((self.patient_state_old, np.copy(self.cache)))
                self.patient_state_old = self.patient_state
                self.cache = np.zeros((self.cache_size, 73))
                cache_index = 0
            
            # if timestamp exists, add sample to the cache
            if timestamp:
                sample_index = len(self.memory[self.patient_state])
                
                big_sample = np.zeros(dataset_width)
                # add ecog data
                big_sample[0:channel_sample] = np.asarray(sample)
                # add timestemp
                big_sample[channel_timestemp-1] = timestamp
                # add patient_state
                big_sample[channel_patient_state-1] = self.patient_state
                # add picture_pause
                big_sample[channel_picture_pause-1] = self.picture_pause
                # add picture_state
                big_sample[channel_picture_state-1] = self.picture_state
                
                # put big_sample into the memory
                self.cache[cache_index, :] = big_sample
                self.memory[self.patient_state].append(big_sample)
                cache_index += 1
                
                if self.picture_pause:
                    self.index_pause = (sample_index - 1, self.patient_state)
                    self.picture_pause = 0
                if self.picture_state == 1:
                    self.index_picture_start = (sample_index, self.patient_state)
                elif self.picture_state == 2:
                    self.index_picture_stop = (sample_index, self.patient_state)
                    if self._good_picture():
                        self.picture_indices[self.patient_state].append((self.index_picture_start[0], self.index_picture_stop[0]))
                self.picture_state = 0
                    
        self.output_queue.put((3, None))
        self._printm('Stop recording')
        t = time.time()
        self._save()
        self._printm('Data saved: {}s:'.format(time.time()-t))
        #inlet.close_stream()

    def _good_picture(self):
        current_state = self.patient_state == self.index_picture_stop[1]
        same_patient_state = self.index_picture_start[1] == self.index_picture_stop[1]
        pause_not_inside_picture = not (self.index_picture_start[1] == self.index_pause[1] and \
                                self.index_picture_start[0] <= self.index_pause[0])
        return current_state and same_patient_state and pause_not_inside_picture


    def _save(self):
        experiment_data_path = Path(self.tool_config.Patient.ExperimentDataPath)
        dataset_width = self.tool_config.Recorder.DatasetWidth
        groups = self.tool_config.Recorder.Groups.split(' ')
        with h5py.File(experiment_data_path, 'w') as file:
            for i in range(len(self.memory)):
                if len(self.memory[i]) > 0:
                    stacked_data = np.vstack(self.memory[i])
                    if len(self.picture_indices[i]) > 0:
                        stacked_indices = np.vstack(self.picture_indices[i])
                    elif i == 0:
                        stacked_indices = np.array([0, stacked_data.shape[0]-1]).reshape((1,2))
                    else:
                        stacked_indices = np.array(()).reshape((0,2))
                    file[groups[i]+'/raw_data'] = stacked_data
                    file[groups[i]+'/picture_indices'] = stacked_indices
                    self.memory[i] = []
                    self.picture_indices[i] = []
                    self._printm('Saved {}, {}, {} pictures'.format(groups[i], stacked_data.shape, stacked_indices.shape[0]))
                else:
                    empty_shape = (0, dataset_width)
                    file.create_dataset(groups[i]+'/raw_data', empty_shape)
                    file.create_dataset(groups[i]+'/picture_indices', (0, 2))
                    self._printm('Saved {}, {}'.format(groups[i], empty_shape))
            file.create_dataset('fs', data=np.array(self.tool_config.Recorder.Frequency))
            

    # resolve commands from Display object to navigate recording of data
    def _resolve_q(self):
        while not self.input_queue.empty():
            key, value = self.input_queue.get()
            
            if key == 'inlet_state':
                self.inlet_state = value
            elif key == 'patient_state':
                self.patient_state = value
            elif key == 'picture_state':
                self.picture_state = value
            elif key == 'pause':
                self.pause = value
            else:
                self._printm('wrong key in queue: {}'.format(key))

    def _printm(self, message):
        print('{} {}: '.format(time.strftime('%H:%M:%S'), type(self).__name__) + message)

    








