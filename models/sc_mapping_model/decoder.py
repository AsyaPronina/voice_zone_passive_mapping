# -*- coding: utf-8 -*-
"""
Created on Thu Aug 13 13:55:15 2020

@author: AlexVosk
"""

from os import makedirs
import time
from pathlib import Path

import numpy as np
import numpy.ma as ma
from matplotlib import pyplot as plt
import h5py
from scipy import signal 
from sklearn.metrics import mutual_info_score

from filterEMG import filterEMG, butter_bandstop_filter
from resultplot import ResultPlot
from math_models import get_model

class Decoder():
    def __init__(self, tool_config, input_queue=None):
        self.recorder = None #rudiment

        self.input_queue = input_queue
        
        self.GRID_X = tool_config.Decoder.GridWidth
        self.GRID_Y = tool_config.Decoder.GridHeight
        self.TH50HZ = tool_config.Decoder.Th50hz
        self.FMAX   = tool_config.Decoder.FMax
        self.FMIN   = tool_config.Decoder.FMin
        self.FSTEP  = tool_config.Decoder.FStep
        self.nchannels = self.GRID_X * self.GRID_Y
        self.GRID_CHANNEL_FROM = tool_config.Decoder.GridChannelFrom
        self.DATA_GROUPS = tool_config.Recorder.Groups.split(' ')
        self.fbandmins = np.arange(self.FMIN, self.FMAX, self.FSTEP)
        self.fbandmaxs = self.fbandmins + self.FSTEP
        self.use_interval = tool_config.Decoder.UseInterval
        self.INTERVAL_START = tool_config.Decoder.IntervalStart
        self.INTERVAL_STOP  = tool_config.Decoder.IntervalStop
        self.single_picture_time = tool_config.Presentation.Duration.Picture

        # create direcoties based on path
        self.experiment_data_path = tool_config.Patient.ExperimentDataPath
        self.results_path = Path(tool_config.Patient.ResultsPath)
        makedirs(self.results_path, exist_ok=True)
        self.path_to_results_file = self.results_path/'score_1.h5'
        self.path_to_results_picture = self.results_path/'score_1.png'
        file_name_number = 1
        while self.path_to_results_file.is_file() or self.path_to_results_picture.is_file():
            file_name_number += 1
            self.path_to_results_file = Path(tool_config.Patient.ResultsPath)/('score_{}.h5'.format(file_name_number))
            self.path_to_results_picture = Path(tool_config.Patient.ResultsPath)/('score_{}.png'.format(file_name_number))
        
        self.measure = tool_config.Decoder.Measure
        
        self.plot_dict = {'mi': np.zeros(self.nchannels),
                 'noise': np.zeros(self.nchannels),
                 'obj6080': np.zeros(self.nchannels),
                 'obj80100': np.zeros(self.nchannels),
                 'obj100120': np.zeros(self.nchannels),
                 'act6080': np.zeros(self.nchannels),
                 'act80100': np.zeros(self.nchannels),
                 'act100120': np.zeros(self.nchannels)}
        #self.rp = ResultPlot(tool_config, self.plot_dict)
        self.use_samples = False
        self.srate = 4096
        self.mixing_time = 8

        self.ecog_50hz_av_cumm = None

    def get_input_queue(self):
        return self.input_queue

    def set_input_queue(self, input_queue):
        self.input_queue = input_queue

    def _make_filters(self, nchannels, srate):
        filter_dict = {}
        # ecog filters
        filter_dict['bnoise50bp'], filter_dict['anoise50bp'] = signal.butter(3, np.array([48, 52])/(srate/2), btype='bandpass')
        filter_dict['bnoise50env'], filter_dict['anoise50env'] = signal.butter(5, 2/(srate/2), btype='low')
        filter_dict['zinoise50bp'] = np.repeat(signal.lfilter_zi(filter_dict['bnoise50bp'], filter_dict['anoise50bp']), nchannels).reshape(-1, nchannels)
        filter_dict['zinoise50env'] = np.repeat(signal.lfilter_zi(filter_dict['bnoise50env'], filter_dict['anoise50env']), nchannels).reshape(-1, nchannels)

        # notch 50, 100, 150 Hz
        filter_dict['bnotch50'], filter_dict['anotch50'] = signal.iirnotch(50, Q = 10, fs = srate)
        filter_dict['bnotch100'], filter_dict['anotch100'] = signal.iirnotch(100, Q = 10, fs = srate)
        filter_dict['bnotch150'], filter_dict['anotch150'] = signal.iirnotch(150, Q = 10, fs = srate)
        filter_dict['zinotch50'] = np.repeat(signal.lfilter_zi(filter_dict['bnotch50'], filter_dict['anotch50']), nchannels).reshape(-1, nchannels)
        filter_dict['zinotch100'] = np.repeat(signal.lfilter_zi(filter_dict['bnotch100'], filter_dict['anotch100']), nchannels).reshape(-1, nchannels)
        filter_dict['zinotch150'] = np.repeat(signal.lfilter_zi(filter_dict['bnotch150'], filter_dict['anotch150']), nchannels).reshape(-1, nchannels)
        # gamma for MI
        filter_dict['bgamma'], filter_dict['agamma'] = signal.butter(3, 20/(srate/2), btype='high')
        filter_dict['zigamma'] = np.repeat(signal.lfilter_zi(filter_dict['bgamma'], filter_dict['agamma']), nchannels).reshape(-1, nchannels)
        # sound filters
        filter_dict['bhp'], filter_dict['ahp'] = signal.butter(3, 200/(srate/2), btype='high', analog=False)
        filter_dict['blp'], filter_dict['alp'] = signal.butter(3, 200/(srate/2), btype='low', analog=False)
        filter_dict['zihp'] = signal.lfilter_zi(filter_dict['bhp'], filter_dict['ahp'])
        filter_dict['zilp'] = signal.lfilter_zi(filter_dict['blp'], filter_dict['alp'])
        return filter_dict
    

    def filter_chunk(self, chunk, ch_idxs_ecog, nchannels, filter_dict):
        chunk_ecog = chunk[:, ch_idxs_ecog]
        chunk_sound = chunk[:, 64]
        # noise estimate
        chunk_ecog_noise_f, filter_dict['zinoise50bp'] = signal.lfilter(filter_dict['bnoise50bp'], filter_dict['anoise50bp'], chunk_ecog, zi=filter_dict['zinoise50bp'], axis=0)
        chunk_ecog_noise_abs = np.abs(chunk_ecog_noise_f)
        chunk_ecog_noise_env, filter_dict['zinoise50env'] = signal.lfilter(filter_dict['bnoise50env'], filter_dict['anoise50env'], chunk_ecog_noise_abs, zi=filter_dict['zinoise50env'], axis=0)
        # notch 50, 100, 150 Hz
        chunk_ecogf, filter_dict['zinotch50'] = signal.lfilter(filter_dict['bnotch50'], filter_dict['anotch50'], chunk_ecog, zi=filter_dict['zinotch50'], axis=0)
        chunk_ecogf, filter_dict['zinotch100'] = signal.lfilter(filter_dict['bnotch100'], filter_dict['anotch100'], chunk_ecogf, zi=filter_dict['zinotch100'], axis=0)
        chunk_ecogf, filter_dict['zinotch150'] = signal.lfilter(filter_dict['bnotch150'], filter_dict['anotch150'], chunk_ecogf, zi=filter_dict['zinotch150'], axis=0)
        # gamma for MI
        chunk_ecog_mi, filter_dict['zigamma'] = signal.lfilter(filter_dict['bgamma'], filter_dict['agamma'], chunk_ecogf, zi=filter_dict['zigamma'], axis=0)
        # sound
        chunk_soundf, filter_dict['zihp']  = signal.lfilter(filter_dict['bhp'], filter_dict['ahp'], chunk_sound, zi=filter_dict['zihp'])
        chunk_soundf, filter_dict['zilp'] = signal.lfilter(filter_dict['blp'], filter_dict['alp'], np.log(np.abs(chunk_soundf)), zi=filter_dict['zilp'])
        return chunk_ecog_noise_env, chunk_ecog_mi, chunk_ecogf, chunk_soundf


    def process_current_file(self):
        processed_data = self.process_file(self.experiment_data_path)
        score_obj = self.prediction_score(processed_data[self.DATA_GROUPS[0]],
                                       processed_data[self.DATA_GROUPS[1]],
                                       get_model(self.measure))
        score_act = self.prediction_score(processed_data[self.DATA_GROUPS[0]],
                                       processed_data[self.DATA_GROUPS[2]],
                                       get_model(self.measure))
        return score_obj, score_act
        #self.save_score(self.DATA_GROUPS[1], score_obj.values)
        #self.save_score(self.DATA_GROUPS[2], score_act.values)
        #self.plot_results([score_obj, score_act], processed_data)
        

    def process_file(self, path):
        print(path)
        processed_data = {}
        for group in self.DATA_GROUPS:
            self._printm('Processing ' + group);
            with h5py.File(path,'r+') as file:
                raw_data = np.array(file[group]['raw_data'])
                picture_indices = np.array(file[group]['picture_indices'])
                srate = int(file['fs'][()])
            processed_data[group] = self._process_data(group, raw_data, picture_indices, srate)
        return processed_data

    def decode(self):
        mi_main, mi_ref, ecog_50hz_av_cumm = self.process_realtime()
        self.ecog_50hz_av_cumm = ecog_50hz_av_cumm
        # need to split to another function

    # Should be called in the end after recording
    def decode_finish(self):
        #self.recorder.thread.join()
        # score_obj, score_act = self.process_current_file()
        # #self.plot_dict['mi'] = mi_main - mi_ref
        # self.plot_dict['noise'] = self.ecog_50hz_av_cumm
        # self.plot_dict['obj6080'] = score_obj[:,0] 
        # self.plot_dict['obj80100'] = score_obj[:,1]         
        # self.plot_dict['obj100120'] = score_obj[:,2] 
        # self.plot_dict['act6080'] = score_act[:,0] 
        # self.plot_dict['act80100'] = score_act[:,1] 
        # self.plot_dict['act100120'] = score_act[:,2] 
        #self.rp.make_figure_full()
        pass
       
        

    def process_realtime(self):
        
        mi_main, mi_ref, ecog_50hz_av_cumm = None, None, None
        
        #self.rp.make_figure_realtime()
        #self.rp.update()
        
        
        ch_idxs_ecog = np.arange(self.GRID_CHANNEL_FROM, self.GRID_CHANNEL_FROM + self.nchannels) - 1
        
        chunks_ecog_mi = []
        chunks_sound = []
        self.ecog = [[], [], []]
        
        mi_main = np.zeros(self.nchannels)
        ecog_50hz_av_cumm = np.zeros(self.nchannels)
        
        self.filter_dict = self._make_filters(self.nchannels, self.srate)

        chunk_id = 0
        while True:
            if self.input_queue.empty():
                time.sleep(0.01)
                continue
            else:
                patient_state, chunk = self.input_queue.get()
                #print('got:', patient_state)
                
            if patient_state == 3:
                break
            
            chunk_filtered = self.filter_chunk(chunk, ch_idxs_ecog, self.nchannels, self.filter_dict)
            chunk_ecog_noise_env, chunk_ecog_mi, chunk_ecogf, chunk_sound = chunk_filtered

            # if it is the first chunk - skip it due to the transition processes
            if chunk_id == 0:
                chunk_id += 1
                continue
            
            # deal with noise
            chunk_ecog_50hz_av = np.mean(chunk_ecog_noise_env, axis = 0)
            #print(chunk_ecog_50hz_av[:5])
            #continue
            
            ecog_50hz_av_cumm = ecog_50hz_av_cumm*((chunk_id-1)/chunk_id) + chunk_ecog_50hz_av/chunk_id # need to plot that
            #ecog_50hz_av_cumm = ecog_50hz_av
            
            #ecog_50hz_av = chunk_ecog_50hz_av
            #bad_ch = ecog_50hz_av > self.TH50HZ
            self.plot_dict['noise'] = chunk_ecog_50hz_av
            # call some plotting method
            
            self.ecog[patient_state].append(chunk_ecogf)
        
        
            if patient_state >= 1:
                chunks_ecog_mi.append(chunk_ecog_mi)
                chunks_sound.append(chunk_sound)
                if len(chunks_ecog_mi) == self.mixing_time:
                    if self.use_samples:
                        mi_main, mi_ref, hists_main, hists_samples, edges_ecog, edges_sound = self.mi_estimation_base_samples(chunks_ecog_mi, chunks_sound, chunk_ecog_mi, chunk_sound, nsamples=64, nbins=30)
                    else:
                        mi_main, mi_ref, hists_main, hists_samples, edges_ecog, edges_sound = self.mi_estimation_base_reverse(chunks_ecog_mi, chunks_sound, chunk_ecog_mi, chunk_sound, nbins=30)
                    self.plot_dict['mi'] = mi_main - mi_ref
                elif len(chunks_ecog_mi) > self.mixing_time:
                    if self.use_samples:
                        self.mi_main, mi_ref, hists_main, hists_samples = self.mi_estimation_update_samples(chunks_ecog_mi, chunks_sound, hists_main, hists_samples, edges_ecog, edges_sound, nsamples=64)
                    else:
                        mi_main, mi_ref, hists_main, hists_samples = self.mi_estimation_update_reverse(chunks_ecog_mi, chunks_sound, hists_main, hists_samples, edges_ecog, edges_sound)
                    
                    self.plot_dict['mi'] = (mi_main - mi_ref > 0)*(mi_main - mi_ref)
            #self.rp.update()
        return mi_main, mi_ref, ecog_50hz_av_cumm
        
            
            
        
    def mi_estimation_base_samples(self, chunks_ecog_mi, chunks_sound, chunk_ecog_mi, chunk_sound, nsamples, nbins):
        base_size = len(chunks_ecog_mi)
        
        def make_derangements(nsamples, base_size):
            np.random.seed(42)
            derangements = []
            while len(derangements) < nsamples:
                permutation = np.random.permutation(base_size)
                if np.sum(permutation==base_size) == 0:
                    derangements.append(permutation)
            return derangements
        derangements = make_derangements(nsamples, base_size)
        
        ecog_base = np.concatenate(chunks_ecog_mi, axis=0)
        sound_base = np.concatenate(chunks_sound)
        hists_main, edges_ecog, edges_sound = [], [], []
        mi_main, mi_samples = np.zeros(self.nchannels), np.zeros(nsamples, self.nchannels)
        
        for i in range(self.nchannels):
            hist_main, edge_ecog, edge_sound = np.histogram2d(ecog_base[:,i], sound_base, nbins)
            hists_main.append(hist_main)
            edges_ecog.append(edge_ecog)
            edges_sound.append(edge_sound)
            mi_main[i] = mutual_info_score(None, None, contingency=hists_main[i])
        
        hists_samples = [[None for _ in range(self.nchannels)] for _ in range(nsamples)]
        for j in range(nsamples):
            sound_sample = np.concatenate([chunks_sound[k] for k in derangements[j]])
            for i in range(self.nchannels):
                hist_sample, _, _ = np.histogram2d(ecog_base[:,i], sound_sample, bins=(edges_ecog[i], edges_sound[i]))
                hists_samples[j][i] = hist_sample
                mi_samples[j,i] = mutual_info_score(None, None, contingency=hist_sample)
        mi_ref = np.quantile(mi_samples, 0.95, axis=0)
        return mi_main, mi_ref, hists_main, hists_samples, edges_ecog, edges_sound
    
    
    def mi_estimation_update_samples(self, chunks_ecog_mi, chunks_sound, hists_main, hists_samples, edges_ecog, edges_sound, nsamples):
        chunk_ecog = chunks_ecog_mi[-1]
        chunk_sound = chunks_sound[-1]

        mi_main = np.zeros(self.nchannels)
        for i in range(self.nchannels):
            hist_main, _, _ = np.histogram2d(chunk_ecog[:,i], chunk_sound, bins=(edges_ecog[i], edges_sound[i]))
            hists_main[i] += hist_main
            mi_main[i] = mutual_info_score(None, None, contingency=hists_main[i])
            
        mi_samples = np.zeros((nsamples, self.nchannels))
        for j in range(nsamples):
            sound_choice = np.random.choice(len(chunks_sound)-1)
            for i in range(self.nchannels):
                hist_sample, _, _ = np.histogram2d(chunk_ecog[:,i], chunks_sound[sound_choice][:chunk_ecog.shape[0]], bins=(edges_ecog[i], edges_sound[i]))
                hists_samples[j][i] += hist_sample
                mi_samples[j,i] = mutual_info_score(None, None, contingency=hists_samples[j][i])
        mi_ref = np.quantile(mi_samples, 0.95, axis=0)
        return mi_main, mi_samples, hists_main, hists_samples
        
    
    
    def mi_estimation_base_reverse(self, chunks_ecog_mi, chunks_sound, chunk_ecog_mi, chunk_sound, nbins):
        base_size = len(chunks_ecog_mi)
        
        ecog_base = np.concatenate(chunks_ecog_mi, axis=0)
        ecog_base_reverse = ecog_base[::-1,:]
        hists_main, hists_reverse, edges_ecog, edges_sound = [], [], [], []
        sound_base = np.concatenate(chunks_sound)
        mi_main, mi_ref = np.zeros(self.nchannels), np.zeros(self.nchannels)
        
        for i in range(self.nchannels):
            hist_main, edge_ecog, edge_sound = np.histogram2d(ecog_base[:,i], sound_base, nbins)
            hists_main.append(hist_main)
            edges_ecog.append(edge_ecog)
            edges_sound.append(edge_sound)
            mi_main[i] = mutual_info_score(None, None, contingency=hist_main)
        for i in range(self.nchannels):
            hist_reverse, edge_ecog, edge_sound = np.histogram2d(ecog_base_reverse[:,i], sound_base, nbins)
            hists_reverse.append(hist_main)
            mi_ref[i] = mutual_info_score(None, None, contingency=hist_reverse)
            
        return mi_main, mi_ref, hists_main, hists_reverse, edges_ecog, edges_sound
    
    
    def mi_estimation_update_reverse(self, chunks_ecog_mi, chunks_sound, hists_main, hists_reverse, edges_ecog, edges_sound):
        chunk_ecog = chunks_ecog_mi[-1]
        chunk_ecog_reverse = chunk_ecog[::-1,:]
        chunk_sound = chunks_sound[-1]

        mi_main = np.zeros(self.nchannels)
        for i in range(self.nchannels):
            hist_main, _, _ = np.histogram2d(chunk_ecog[:,i], chunk_sound, bins=(edges_ecog[i], edges_sound[i]))
            hists_main[i] += hist_main
            mi_main[i] = mutual_info_score(None, None, contingency=hists_main[i])
            
        mi_reverse = np.zeros(self.nchannels)
        for i in range(self.nchannels):
            sound_choice = np.random.choice(len(chunks_sound)-1)
            hist_reverse, _, _ = np.histogram2d(chunk_ecog_reverse[:,i], chunks_sound[sound_choice][:chunk_ecog_reverse.shape[0]], bins=(edges_ecog[i], edges_sound[i]))
            hists_reverse[i] += hist_reverse
            mi_reverse[i] = mutual_info_score(None, None, contingency=hists_reverse[i])
        mi_ref = mi_reverse
        return mi_main, mi_ref, hists_main, hists_reverse
        
    
    
    
    
    
    
    
    
    
    # process raw data,         
    def _process_data(self, name, raw_data, picture_indices, srate):
        # range of channels with eeg data, e.g. for grid 1 to 20 => range(0, 20) ~ [0, 1, ..., 19]
        ch_idxs_ecog = np.arange(self.GRID_CHANNEL_FROM, self.GRID_CHANNEL_FROM + self.nchannels) - 1
        
        # copy ecog and stim data
        data_ecog = np.copy(raw_data[:,ch_idxs_ecog])
        
        # get 50hz averege of data
        ecog_50hz_av = np.mean(filterEMG(data_ecog, 48, 52, srate), axis = 0)
        
        # bad channels - array where 50hz average is > threshold        
        bad_ch = ecog_50hz_av > self.TH50HZ
            
        # notch-filter power-line (remove 50hz from good channels)
        for channel in range(data_ecog.shape[1]):
            if channel not in bad_ch:
                for freq in np.arange(50,200,50):
                    data_ecog[:,channel] = butter_bandstop_filter(data_ecog[:,channel], freq-2, freq+2, srate, 4)
        
        return ProcessedData(name = name,
                             data_ecog=data_ecog, 
                             picture_indices=picture_indices, 
                             ecog_50hz_av=ecog_50hz_av,
                             bad_ch=bad_ch, 
                             srate=srate)


    def prediction_score(self, data_i, data_j, model, *args, **kwargs):
        # matricies to store score
        score = np.zeros((self.nchannels, len(self.fbandmins)))
        
        def indices(data):
            ind = np.zeros(0)
            for start, stop in data.picture_indices:
                start, stop = int(start), int(stop)
                length = stop - start
                interval_start = int(start + length * self.INTERVAL_START/self.single_picture_time)
                interval_stop = int(start + length * self.INTERVAL_STOP/self.single_picture_time)
                if interval_start < interval_stop:
                    ind = np.append(ind, np.arange(interval_start, interval_stop))
            ind = ind.astype(int)
            return ind
        
        if self.use_interval:
            indj = indices(data_j)
        else:
            indj = np.arange(data_j.data_ecog.shape[0])
        
        #print(indj)
        #if data_i.data_ecog.shape[0] > indj.shape[0]:
        #    left_shift_base = 2 * data_i.srate
        #    shift = (data_i.data_ecog.shape[0] - indj.shape[0])//2
        #    left_shift = shift if shift > left_shift_base else left_shift_base
        #    indi = np.arange(left_shift, )
        #indi = np.arange(data_i.srate * 30, min(data_i.data_ecog.shape[0], indj.shape[0]))
        indi = np.arange(data_i.srate * 1, data_i.data_ecog.shape[0])
        
        #xis = np.zeros((indi.shape[0], self.nchannels, len(self.fbandmins)))
        #xjs = np.zeros((indj.shape[0], self.nchannels, len(self.fbandmins)))
        # if there is no pictures
        if indi.shape[0] == 0:
            #print('return zeros')
            return Score(values = score,
                         data_i = data_i,
                         data_j = data_j)
        
        #bad_channels = np.logical_or(data_i.bad_ch, data_j.bad_ch)
        for freq_index in range(len(self.fbandmins)):
            fbandmin = self.fbandmins[freq_index]
            fbandmax = self.fbandmaxs[freq_index]
            
            #xi1 = filterEMG(data_i.data_ecog, fbandmin, fbandmax, data_i.srate)
            #print(xi1.shape, indi)
            #print(indi)
            xi = filterEMG(data_i.data_ecog, fbandmin, fbandmax, data_i.srate)[indi]
            xj = filterEMG(data_j.data_ecog, fbandmin, fbandmax, data_j.srate)[indj]
            
            #xis[:, :, freq_index] = np.copy(xi)
            #xjs[:, :, freq_index] = np.copy(xj)
            for channel in range(self.nchannels): 
                #if not bad_channels[channel]:
                score[channel, freq_index] = model(xi[:,[channel]], xj[:,[channel]], args, kwargs)
        #score[bad_channels, :] = 0            
        return score
        #return Score(values = score,
        #             data_i = data_i,
         #            data_j = data_j,
        #             xi = xis,
        #            xj = xjs)

    def save_score(self, name, data):
        with h5py.File(self.path_to_results_file, 'a') as file:
            file[name] = data

    def plot_results(self, scores, data):
        plt.close('all')
        plot_shape = (len(scores) + 1, scores[0].values.shape[1])
        fig, ax = plt.subplots(nrows = plot_shape[0],
                               ncols = plot_shape[1],
                               figsize=(12,8))
        
        def get_minmax_score(scores):
            min_score, max_score = 0, 0.3
            for score in scores:
                min_score = np.amin(score.values) if np.amin(score.values) < min_score else min_score
                max_score = np.amax(score.values) if np.amax(score.values) > max_score else max_score
            return min_score, max_score
        min_score, max_score = get_minmax_score(scores)
        
        row_titles = ['R^2 objects', 'R^2 actions', '50Hz']
        col_titles = self.DATA_GROUPS
        
        viridis_cm = plt.cm.get_cmap('viridis', 256)
        viridis_cm.set_bad('black', 1)

        def array_into_grid(array):
            return (array.reshape([self.GRID_X,self.GRID_Y]).T)[::-1,:]
        
        ecog_channel_grid = array_into_grid(np.arange(self.GRID_CHANNEL_FROM, self.GRID_CHANNEL_FROM + self.nchannels))
        print(ecog_channel_grid)
        for i in range(plot_shape[0] - 1):
            for j in range(plot_shape[1]):
                plt.subplot(plot_shape[0], plot_shape[1], (i*plot_shape[1] + j + 1))  
                
                im = array_into_grid(scores[i].values[:,j])                
                bad_channels = np.logical_or(scores[i].data_i.bad_ch, scores[i].data_j.bad_ch)                
                im_masked = ma.masked_array(im, array_into_grid(bad_channels))

                plt.imshow(im_masked, cmap = viridis_cm, vmin=min_score, vmax=max_score)
                plt.colorbar()
                
                for m in range(self.GRID_Y):
                    for n in range(self.GRID_X):
                        plt.text(n, m, str(ecog_channel_grid[m,n]), color='white', ha='center', va='center' )
                plt.plot([0.5, 0.5], [-0.5, 1.5], color='silver', lw=2)
                plt.plot([2.5, 2.5], [-0.5, 1.5], color='silver', lw=2)
                plt.title(str(self.fbandmins[j])+'-'+str(self.fbandmaxs[j])+ ' Hz');
                if j == 0:
                    plt.text(-10, 5, row_titles[i], size = 24)
                plt.axis("off")
        
        
        
        for j in range(plot_shape[1]):
            plt.subplot(3, plot_shape[1], plot_shape[1]*2 + (j+1))
            im = array_into_grid(data[self.DATA_GROUPS[j]].ecog_50hz_av)
            plt.imshow(im)
            plt.colorbar();
            for m in range(self.GRID_Y):
                for n in range(self.GRID_X):
                    plt.text(n, m, str(ecog_channel_grid[m,n]), color='white', ha='center', va='center' )
            plt.plot([0.5, 0.5], [-0.5, 1.5], color='silver', lw=2)
            plt.plot([2.5, 2.5], [-0.5, 1.5], color='silver', lw=2)
            plt.title(col_titles[j]);
            if j == 0:
                plt.text(-8, 5, row_titles[2], size = 24)
            plt.axis("off")
        
        fig.tight_layout()
        plt.savefig(self.path_to_results_picture)
        plt.show()

    def _printm(self, message):
        print('{} {}: '.format(time.strftime('%H:%M:%S'), type(self).__name__) + message)



class ProcessedData:
    def __init__(self, name, data_ecog, picture_indices, ecog_50hz_av, bad_ch, srate):
        self.name = name
        self.data_ecog = data_ecog
        self.picture_indices = picture_indices
        self.ecog_50hz_av = ecog_50hz_av
        self.bad_ch = bad_ch
        self.srate = srate

    def __repr__(self):
        result = ''
        result += self.name + '\n'
        result += 'data_ecog shape: ' + str(self.data_ecog.shape) + '\n'
        result += 'picture_indices shape: ' + str(self.picture_indices.shape) + '\n'
        result += 'number of bad_ch: ' + str(np.sum(self.bad_ch)) + '\n'
        result += 'srate: ' + str(self.srate) + '\n'
        return result
    


class Score:
    def __init__(self, values, data_i, data_j, xi = None, xj = None):
        self.values = values
        self.data_i = data_i
        self.data_j = data_j
        self.xi = xi
        self.xj = xj

