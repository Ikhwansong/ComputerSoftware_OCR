# -*- coding: utf-8 -*-
"""
Created on Thu Jun 11 10:46:58 2020

@author: dlrgh
"""


#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May 31 17:01:21 2020

@author: ihsong
"""

import cv2
import numpy as np
from matplotlib import pyplot as plt
from easydict import EasyDict 
import os
import glob


# def load_img_and_scissor(img_path):    
#     scene = cv2.imread(img_path,0)
#     scene_reverser = 255 - scene
#     scene_height, scene_width = scene.shape
#     hist_graph = scene_reverser.sum(axis = 1) /scene_width   

#     if np.sum(hist_graph) > 255 * scene_height * 0.5 :
#         hist_graph = scene.sum(axis = 1) /scene_width 
    
#     #x = range(len(hist_graph))
#     #plt.plot(x, hist_graph)
    
    
#     threshold = 1
#     area = 0
#     flag = 'end'
#     start_index, end_index = 0,0
#     section_dict = EasyDict()
#     scene_num = 0 
#     for index, value in enumerate(hist_graph):    
#         if value > threshold :        
#             if flag == 'end' :
#                 start_index = index

#                 #print("start index : ",start_index )
#                 flag = 'start'
#             if flag == 'start' :
#                 #print('value : ',value)
#                 area = area + value
#         else :
#             if flag == 'start':
#                 #print("end index : ", index)
#                 end_index = index
#                 area = area / (end_index - start_index) 
#                 flag = 'end'
#                 if area > 30:
#                     sec_num = 'sec_{}'.format(scene_num)
#                     section_dict[sec_num] = {'start_index': start_index}
#                     sec_num = 'sec_{}'.format(scene_num)
#                     section_dict[sec_num].end_index = index
#                     section_dict[sec_num].area = area
#                     scene_num = scene_num + 1                
#                 #print("area : ", area)
#                 area = 0         
#     return section_dict

# def read_dict_and_save_img(scene_path, section_dict, save_path):
#     img = cv2.imread(scene_path)
#     for section_key in section_dict :
#         try :
#             img_height = section_dict[section_key].end_index - section_dict[section_key].start_index 
#             if img_height > 170 :
#                 cv2.imwrite(os.path.join(save_path, os.path.basename(scene_path) + '_' + section_key) +'.png', img[section_dict[section_key].start_index -110 : section_dict[section_key].end_index +110, :, : ])
#         except :
#             print("Problem scene: ", scene_path)
     
# webtoon_folder_path = glob.glob('./개같은 세상/*')
# save_path = '.\\'
# folder_name = 'webtoon_scissored'
# full_path = os.path.join(save_path, folder_name)
# print("full_path : ", full_path)
# os.makedirs(full_path, exist_ok=True)
# for episode_path in webtoon_folder_path : 
#     print("Episode _path : ", episode_path)
#     os.makedirs(os.path.join(full_path,os.path.basename(episode_path)), exist_ok='True')
#     for scene_path in glob.glob(episode_path +'/*') :
        
#         scene_path = r'{}'.format(scene_path)
#         scene_path = scene_path.replace('/', '\\')
#         print("scene_path : ", scene_path)
#         scissored_dict = load_img_and_scissor(scene_path)
#         if len(scissored_dict) > 0 :
#             read_dict_and_save_img(scene_path, scissored_dict, os.path.join(full_path,os.path.basename(episode_path) ))
        
    


#--- windows ---#

def load_img_and_scissor(img_path):    
    scene = cv2.imread(img_path,0)
    scene_reverser = 255 - scene
    scene_height, scene_width = scene.shape
    hist_graph = scene_reverser.sum(axis = 1) /scene_width   

    if np.sum(hist_graph) > 255 * scene_height * 0.5 :
        hist_graph = scene.sum(axis = 1) /scene_width 
    
    #x = range(len(hist_graph))
    #plt.plot(x, hist_graph)
    
    
    threshold = 1
    area = 0
    flag = 'end'
    start_index, end_index = 0,0
    section_dict = EasyDict()
    scene_num = 0 
    for index, value in enumerate(hist_graph):    
        if value > threshold :        
            if flag == 'end' :
                start_index = index

                #print("start index : ",start_index )
                flag = 'start'
            if flag == 'start' :
                #print('value : ',value)
                area = area + value
        else :
            if flag == 'start':
                #print("end index : ", index)
                end_index = index
                area = area / (end_index - start_index) 
                flag = 'end'
                if area > 30:
                    sec_num = 'sec_{}'.format(scene_num)
                    section_dict[sec_num] = {'start_index': start_index}
                    sec_num = 'sec_{}'.format(scene_num)
                    section_dict[sec_num].end_index = index
                    section_dict[sec_num].area = area
                    scene_num = scene_num + 1                
                #print("area : ", area)
                area = 0         
    return section_dict

def read_dict_and_save_img(scene_path, section_dict, save_path, prefix):
    img = cv2.imread(scene_path)
    for section_key in section_dict :
        try :
            img_height = section_dict[section_key].end_index - section_dict[section_key].start_index 
            if img_height > 170 :
                cv2.imwrite(os.path.join(save_path, prefix + '_' + os.path.splitext(os.path.basename(scene_path))[0] + '_' + section_key) +'.png', img[section_dict[section_key].start_index -110 : section_dict[section_key].end_index +110, :, : ])
        except :
            print("Problem scene: ", scene_path)
     
webtoon_folder_path = glob.glob('./the_world_of_dog/*')
save_path = '.\\'
folder_name = 'webtoon_scissored'
full_path = os.path.join(save_path, folder_name)
print("full_path : ", full_path)
os.makedirs(full_path, exist_ok=True)
for episode_path in webtoon_folder_path : 
    print("Episode _path : ", episode_path)
    os.makedirs(os.path.join(full_path,os.path.basename(episode_path)), exist_ok='True')
    for scene_path in glob.glob(episode_path +'/*') :
        
        scene_path = r'{}'.format(scene_path)
        scene_path = scene_path.replace('\\', '/')
        print("scene_path : ", scene_path)
        scissored_dict = load_img_and_scissor(scene_path)
        if len(scissored_dict) > 0 :
            read_dict_and_save_img(scene_path, scissored_dict, os.path.join(full_path,os.path.basename(episode_path)), os.path.basename(episode_path))
        
    

