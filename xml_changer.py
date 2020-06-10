#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun  5 01:22:42 2020

@author: ihsong
"""
import xml.etree.ElementTree as et



tree = et.ElementTree(file = './data/custom/Annotations/0_sec_1.xml')
root = tree.getroot()

for child in root:
    print('')