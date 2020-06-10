#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun  5 18:49:55 2020

@author: ihsong
"""


import argparse
import tensorflow as tf
import os
import sys
import numpy as np
import yaml
import cv2
from tqdm import tqdm

from anchor import generate_default_boxes
from box_utils import decode, compute_nms
from voc_data import create_batch_generator, create_batch_generator_with_customset, create_batch_generator_with_custom_findarea_set
from image_utils import ImageVisualizer, ImageVisualizer_cv2
from losses import create_losses
from network import create_ssd
from PIL import Image





data_dir = './data/custom_area'
arch_area = 'ssd512'
arch_char = 'ssd300'
num_examples = -1 #This will reduce num of samples from dataset
pretrained_type = 'specified'
checkpoint_dir = ''
checkpoint_findarea_path = './checkpoints_find_area/ssd_epoch_1000.h5'

checkpoint_path = './checkpoints/ssd_epoch_1000.h5'

gpu_id = '0'

os.environ['CUDA_VISIBLE_DEVICES'] = gpu_id

BATCH_SIZE = 1

def predict(imgs, default_boxes ,trigger = None):
    if trigger =='area':
        confs, locs = find_area_ssd(imgs)
        NUM_CLASSES = 2
    else :
        confs, locs = ssd(imgs)
        NUM_CLASSES = 39
    confs = tf.squeeze(confs, 0)
    locs = tf.squeeze(locs, 0)

    confs = tf.math.softmax(confs, axis=-1)
    classes = tf.math.argmax(confs, axis=-1)
    scores = tf.math.reduce_max(confs, axis=-1)

    boxes = decode(default_boxes, locs)

    out_boxes = []
    out_labels = []
    out_scores = []

    for c in range(1, NUM_CLASSES):
        cls_scores = confs[:, c]

        score_idx = cls_scores > 0.6
        # cls_boxes = tf.boolean_mask(boxes, score_idx)
        # cls_scores = tf.boolean_mask(cls_scores, score_idx)
        cls_boxes = boxes[score_idx]
        cls_scores = cls_scores[score_idx]

        nms_idx = compute_nms(cls_boxes, cls_scores, 0.45, 200)
        cls_boxes = tf.gather(cls_boxes, nms_idx)
        cls_scores = tf.gather(cls_scores, nms_idx)
        cls_labels = [c] * cls_boxes.shape[0]

        out_boxes.append(cls_boxes)
        out_labels.extend(cls_labels)
        out_scores.append(cls_scores)

    out_boxes = tf.concat(out_boxes, axis=0)
    out_scores = tf.concat(out_scores, axis=0)

    boxes = tf.clip_by_value(out_boxes, 0.0, 1.0).numpy()
    classes = np.array(out_labels)
    scores = out_scores.numpy()

    return boxes, classes, scores


if __name__ == '__main__':
    with open('./config.yml') as f:
        cfg = yaml.load(f)

    try:
        config_area = cfg[arch_area.upper()]
        config_char = cfg[arch_char.upper()]
    except AttributeError:
        raise ValueError('Unknown architecture: {}'.format(arch_area))

    default_boxes_area = generate_default_boxes(config_area)
    default_boxes_char = generate_default_boxes(config_char)
    

    batch_generator, info = create_batch_generator_with_custom_findarea_set(
        data_dir,
        config_area['image_size'],
        BATCH_SIZE, num_examples, mode='test')

    try:
        find_area_ssd = create_ssd(2, arch_area,
                         pretrained_type,
                         checkpoint_dir,
                         checkpoint_findarea_path)
        ssd = create_ssd(39, arch_char,
                         pretrained_type,
                         checkpoint_dir,
                         checkpoint_path)
    except Exception as e:
        print(e)
        print('The program is exiting...')
        sys.exit()

    os.makedirs('outputs/images', exist_ok=True)
    os.makedirs('outputs/detects', exist_ok=True)
    #visualizer = ImageVisualizer(info['idx_to_name'], save_dir='outputs/images')
    visualizer = ImageVisualizer_cv2(info['idx_to_name'], save_dir='outputs/images')
    
    for i, (filename, imgs) in enumerate(
        tqdm(batch_generator, total=info['length'],
             desc='Testing...', unit='images')):
        print(type(imgs))
        print(imgs.shape)

        area_boxes, _, _ = predict(imgs, default_boxes_area, trigger ='area')
        
        filename = filename.numpy()[0].decode()
        #--- character detection ---#     
        img_path = os.path.join(info['image_dir'], '{}.jpg'.format(filename))   
        original_image = Image.open(img_path)
        area_boxes *= original_image.size *2
        #original_image = cv2.imread(img_path)
        #ori_img_h, ori_img_w, _ = original_image.shape
        #area_boxes *= (ori_img_w, ori_img_h) *2
        
        original_scale_box_list = []
        
        for area_box in area_boxes:
            cutted_img = original_image.crop((area_box[0], area_box[1], area_box[2], area_box[3]))
            #cutted_img = original_image[int(area_box[1]): int(area_box[3]), int(area_box[0]) : int(area_box[2]),:]
            
            cutted_img = np.expand_dims(np.array(cutted_img), axis=0)
            cutted_img = tf.convert_to_tensor(cutted_img, dtype=tf.float32)
            print(cutted_img.shape)
            boxes, classes, scores = predict(cutted_img, default_boxes_char, trigger = 'char')
            
            boxes *= original_image.size *2
            boxes += (area_box[0], area_box[1])
            #boxes *= (ori_img_w, ori_img_h) *2            
            #boxes += (int(area_box[0]), int(area_box[1]))
            
            original_scale_box_list.append(boxes)
            
        original_scale_box_array = np.array(original_scale_box_list).reshape(-1,4)
        
        visualizer.save_image(img_path,original_scale_box_array,classes, '{}.jpg'.format(filename))      
        


