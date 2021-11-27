# -*- coding: utf-8 -*-
"""
Created on Sun Apr 11 10:25:51 2021

@author: AlexVosk
"""

import os
import numpy as np
import cv2 as cv
from threading import Thread
import time
import winsound
import random
import math
from pathlib import Path
from tqdm import tqdm, trange
import matplotlib.pyplot as plt 
from matplotlib.animation import FuncAnimation



class ResultPlot:
    def __init__(self, toolConfig, plot_dict):
        self.plot_dict = plot_dict
        self.GRID_X = toolConfig.Decoder.GridWidth
        self.GRID_Y = toolConfig.Decoder.GridHeight
        self.GRID_CHANNEL_FROM = toolConfig.Decoder.GridChannelFrom

        #ani = FuncAnimation(self.fig, self.update, self.generator_dict(), interval=1000)
        #plt.show()
        
    def array_into_grid(self, array):
        return (array.reshape([self.GRID_X,self.GRID_Y]).T)[:,::-1]

    def make_image(self, ax, data, title):
        
        grid = self.array_into_grid(data)
        img = ax.imshow(grid, cmap = plt.cm.get_cmap('viridis', 256))
        plt.colorbar(img, ax=ax)
        
        ecog_channel_grid = self.array_into_grid(np.arange(self.GRID_CHANNEL_FROM, self.GRID_CHANNEL_FROM + self.GRID_X*self.GRID_Y))
        for m in range(self.GRID_Y):
            for n in range(self.GRID_X):
                ax.text(n, m, str(ecog_channel_grid[m,n]), color='white', ha='center', va='center' )
        
        for i in range(self.GRID_X//2):
            ax.plot([0.5+i*2, 0.5+i*2], [self.GRID_Y-3, self.GRID_Y], color='silver', lw=4)
        
        ax.set_title(title);
        ax.axis("off")
        return img

    def update(self):
        mi = self.array_into_grid(self.plot_dict['mi'])
        noise = self.array_into_grid(self.plot_dict['noise'])

        self.img_mi.autoscale()
        self.img_mi.set_data(mi)
        self.img_no.autoscale()
        self.img_no.set_data(noise)
        
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

    def make_figure_realtime(self):
        plt.ion()
        base = np.zeros((self.GRID_X,self.GRID_Y))

        self.fig = plt.figure(constrained_layout=True, figsize=(10, 5))
        gs = self.fig.add_gridspec(1, 2)
        
        #self.ax_mi = self.fig.add_subplot(gs[:, :1])
        ax_mi = self.fig.add_subplot(gs[:, :1])
        #self.ax_no = self.fig.add_subplot(gs[:, 1:])
        ax_no = self.fig.add_subplot(gs[:, 1:])
        
        self.img_mi = self.make_image(ax_mi, base, title='Mutual information')
        #self.img_mi.autoscale()
    
        self.img_no = self.make_image(ax_no, base, title='Noise 50Hz')
        #self.img_no.autoscale()
    
        #self.ax_obj = [self.fig.add_subplot(gs[2*i:2*i+2, 3:5]) for i in range(0, 3)]
        #self.ax_act = [self.fig.add_subplot(gs[2*i:2*i+2, 5:]) for i in range(0, 3)]
        
        #self.img_mi = self.show_plot(self.ax_mi, base)
        #self.img_no = self.show_plot(self.ax_no, base)
        #self.img_obj, self.img_act = [], []
        
        #for i, ax in enumerate(self.ax_obj):
        #    im = self.show_plot(ax, base)
        #    self.img_obj.append(im)
        #for i, ax in enumerate(self.ax_act):
        #    im = self.show_plot(ax, base)
        #    self.img_act.append(im)
        
        #s = time.time()
        #self.fig.canvas.draw()
        #self.fig.canvas.flush_events()
        
        
        
        
        #print('hey')
        
    def make_figure_full(self, ):
        plt.close('all')
        plt.ioff()
        self.fig = plt.figure(constrained_layout=True, figsize=(14, 12))
        gs = self.fig.add_gridspec(6, 7)
        
        ax_mi = self.fig.add_subplot(gs[:3, :3])
        ax_no = self.fig.add_subplot(gs[3:, :3])
        ax_obj = [self.fig.add_subplot(gs[2*i:2*i+2, 3:5]) for i in range(0, 3)]
        ax_act = [self.fig.add_subplot(gs[2*i:2*i+2, 5:]) for i in range(0, 3)]
        
        self.make_image(ax_mi, self.plot_dict['mi'], title='Mutual information')
        self.make_image(ax_no, self.plot_dict['noise'], title='Noise 50Hz')
        
        data_objects = [self.plot_dict['obj6080'], self.plot_dict['obj80100'], self.plot_dict['obj100120']]
        title_objects = ['Objects 60-80Hz', 'Objects 80-100Hz', 'Objects 100-120Hz']
        for i, ax in enumerate(ax_obj):
            self.make_image(ax, data_objects[i], title=title_objects[i])
            
        data_actions = [self.plot_dict['act6080'], self.plot_dict['act80100'], self.plot_dict['act100120']]
        title_actions = ['Actions 60-80Hz', 'Actions 80-100Hz', 'Actions 100-120Hz']
        for i, ax in enumerate(ax_act):
            self.make_image(ax, data_actions[i], title=title_actions[i])
        
        plt.show()
        
        
        
          
if __name__ == '__main__':
    pass
    #plt.ion()
