#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun  6 02:56:32 2020

@author: ihsong
"""


import xml.etree.ElementTree as ET

test_xml =ET.parse('/mnt/8418CA4F18CA4042/computing_software/webtoon_downloader/test_folder/0_sec_1.xml')


img_size = test_xml.find('size')
width = img_size.find('width')
print(width.text)
width.text = str(1000)

ET.dump(img_size)
test_xml.write('test.xml', encoding='utf-8', xml_declaration=True)

