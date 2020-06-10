#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun  6 01:03:54 2020

@author: ihsong
"""

import cv2
import numpy as np
import os
import glob
import xml.etree.ElementTree as ET


area_anno_list = glob.glob('/mnt/8418CA4F18CA4042/computing_software/webtoon_downloader/dog_characters_text_area_label' + '/*')
txt_anno_list = glob.glob('/home/ihsong/Documents/대학원수업/컴퓨터소프트웨어/ssd-tf2-master/data/custom/Annotations' + '/*')

save_path = '/mnt/8418CA4F18CA4042/computing_software/webtoon_downloader/dog_area_cutted_scene'

txt_anno_path = '/mnt/8418CA4F18CA4042/computing_software/webtoon_downloader/dog_characters_scene_label'
txt_modified_save_path = '/mnt/8418CA4F18CA4042/computing_software/webtoon_downloader/dog_area_cutted_label'

for area_anno_path in area_anno_list :
    
    
    area_objects = ET.parse(area_anno_path).findall('object')
    img_size = ET.parse(area_anno_path).find('size')
    file_name = ET.parse(area_anno_path).find('filename').text
    w, h = float(img_size.find('width').text), float(img_size.find('height').text)
    img_path = ET.parse(area_anno_path).find('path').text
    area_boxes = []
    area_labels = []

    img = cv2.imread(img_path)
    

    
    for k, obj in enumerate(area_objects):
        
        area_name = obj.find('name').text.lower().strip()
        area_bndbox = obj.find('bndbox')
        area_xmin = (int(area_bndbox.find('xmin').text) - 1)
        area_ymin = (int(area_bndbox.find('ymin').text) - 1)
        area_xmax = (int(area_bndbox.find('xmax').text) - 1)
        area_ymax = (int(area_bndbox.find('ymax').text) - 1)
        
        txt_anno_xml = ET.parse(os.path.join(txt_anno_path, os.path.splitext(os.path.basename(area_anno_path))[0] + '.xml'))
        root_tag = txt_anno_xml.getroot()
        img_size = txt_anno_xml.find('size')
        img_width = img_size.find('width')
        img_height = img_size.find('height')
        
        num_of_char = 0
        
        for txt_obj in root_tag.findall('object'):
            name = txt_obj.find('name').text.lower().strip()
            bndbox = txt_obj.find('bndbox')
            xmin = (int(bndbox.find('xmin').text) - 1) 
            ymin = (int(bndbox.find('ymin').text) - 1) 
            xmax = (int(bndbox.find('xmax').text) - 1) 
            ymax = (int(bndbox.find('ymax').text) - 1)            
            center = ((xmin+xmax)/2, (ymin+ymax)/2)
            
            if area_xmin < xmin and area_xmax > xmax and area_ymin < ymin and area_ymax > ymax :
                num_of_char += 1
                img_width.text = str(area_xmax - area_xmin)
                img_height.text = str(area_ymax - area_ymin)
                bndbox.find('xmin').text = str(xmin - area_xmin +1)
                bndbox.find('ymin').text = str(ymin - area_ymin +1)
                bndbox.find('xmax').text = str(xmax - area_xmin +1)
                bndbox.find('ymax').text = str(ymax - area_ymin +1)
            else :
                root_tag.remove(txt_obj)
                
        if num_of_char > 0 :        
            txt_anno_xml.write(os.path.join(txt_modified_save_path, os.path.splitext(file_name)[0] +'_' +str(k) + '.xml'), encoding='utf-8', xml_declaration=True)
            cropped_img = img[area_ymin:area_ymax, area_xmin:area_xmax, :]
            cv2.imwrite(os.path.join(save_path, os.path.splitext(file_name)[0] +'_' +str(k) + os.path.splitext(file_name)[1]), cropped_img )
        else : 
            print("none char activated at : ", os.path.splitext(file_name)[0] +'_' + str(k) +'.xml')
        
    
