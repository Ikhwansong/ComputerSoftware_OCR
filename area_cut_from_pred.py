#!/usr/bin/env python3

# -*- coding: utf-8 -*-

"""

Created on Wed Jun 10 22:29:05 2020

 

@author: ihsong

"""

 

import os
import glob
import cv2

 

img_path = './data/custom_area/PNGImages'
pred_txt_path = './find_area_results/detects/text_area.txt'
save_path = './data/custom/PNGImages' 

os.makedirs('./data/custom/PNGImages', exist_ok=True) 

f = open(pred_txt_path, 'r')
lines = f.readlines()
duplicate_list = {}

for line in lines :

    file_name, x1,y1, x2,y2 = line.split()  
    if file_name in duplicate_list :
        duplicate_list[file_name] +=1 
    else :
        duplicate_list[file_name] = 0

    x1, y1, x2, y2 = int(float(x1)), int(float(y1)), int(float(x2)), int(float(y2))
    img = cv2.imread(os.path.join(img_path,file_name) +'.jpg')
    txt_area = img[y1:y2, x1:x2, :]
    cv2.imwrite(os.path.join(save_path, file_name) + '_'+str(duplicate_list[file_name]) + '.jpeg', txt_area)