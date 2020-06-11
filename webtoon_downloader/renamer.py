#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun  3 15:33:53 2020

@author: ihsong
"""


import os
import glob



folder_list = glob.glob('/mnt/8418CA4F18CA4042/computing_software/webtoon_downloader/dog_characters_scene/*')

for folder_name in folder_list : 
    prefix_name = os.path.basename(folder_name)
    file_list = glob.glob(os.path.join(folder_name, '*'))
    for file_name in file_list : 
        dir_path = os.path.split(file_name)[0]
        new_name = prefix_name + '_' +  os.path.basename(file_name)
        os.rename(file_name, os.path.join(dir_path, new_name))

