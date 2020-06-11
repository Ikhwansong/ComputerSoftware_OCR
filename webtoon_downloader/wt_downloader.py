#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 22 17:38:57 2020

@author: ihsong
"""


"""
For training we have to preprocess the images of webtoon.
In this class, we are going to handle the webtoon which is named "The bastard world like dogs"
Please, Follow my presentation step by step, then you can do it also!
"""

# import os
# import requests
# from PIL import Image
# from bs4 import BeautifulSoup
# from itertools import count

# def NAVER_webtoon_downloader(title_id):

#     # costomized Header
#     headers = {'Referer': 'http://comic.naver.com/index.nhn'}

#     # background color for png file
#     WHITE = (255, 255, 255)

#     # URL for NAVER webtoon
#     url = 'http://comic.naver.com/webtoon/detail.nhn'

#     # for checking last episode
#     ep_list = []

#     for no in count(1):
#         params = {'titleId': title_id, 'no': no}
#         html = requests.get(url, params=params).text
#         soup = BeautifulSoup(html, 'html.parser')

#         # webtoon title & episode title
#         wt_title = soup.select('.detail h2')[0].text
#         ep_title = soup.select('.tit_area h3')[0].text
#         wt_title = wt_title.split()[0]
#         ep_title = ' '.join(ep_title.split()).replace('?', '')

#         # check if this episode is last or not
#         if ep_title in ep_list:
#             break

#         ep_list.append(ep_title)

#         # episode images
#         img_path_list = []

#         img_list = [tag['src'] for tag in soup.select('.wt_viewer > img')]
#         for img in img_list:

#             # save the images
#             img_name = os.path.basename(img)
#             img_path = os.path.join(wt_title, img_name)

#             dir_path = os.path.dirname(img_path)
#             if not os.path.exists(dir_path):
#                 os.makedirs(dir_path)

#             img_path_list.append(img_path)

#             if os.path.exists(img_path):
#                 continue

#             img_data = requests.get(img, headers=headers).content
#             with open(img_path, 'wb') as f:
#                 f.write(img_data)

#         im_list = []
#         for img_path in img_path_list:
#             im = Image.open(img_path)
#             im_list.append(im)

#         # make canvas for appending images
#         canvas_size = (
#             max(im.width for im in im_list),
#             sum(im.height for im in im_list)
#         )
#         canvas = Image.new('RGB', canvas_size)
#         top = 0

#         # save the webtoon
#         for im in im_list:
#             canvas.paste(im, (0, top))
#             top += im.height
#         canvas.save(dir_path + '\/' + ep_title + '.png')

#         # delete all temporally images for webtoon
#         for img_path in img_path_list:
#             os.remove(img_path)

#         print(wt_title + ' ' + ep_title + ' is downloaded.')

#     print('All episode is downloaded completely.')
    
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
import requests
from bs4 import BeautifulSoup


def crawl_naver_webtoon(episode_url):
    html = requests.get(episode_url).text
    soup = BeautifulSoup(html, 'html.parser')

    comic_title = ' '.join(soup.select('.comicinfo h2')[0].text.split()) # ' '.join(['마음의소리', '조석'])
    ep_title = ' '.join(soup.select('.tit_area h3')[0].text.split())

    for img_tag in soup.select('.wt_viewer img'):
        image_file_url = img_tag['src']
        image_dir_path = os.path.join(os.path.dirname(__file__), comic_title, ep_title)
        image_file_path = os.path.join(image_dir_path, os.path.basename(image_file_url))

        if not os.path.exists(image_dir_path):
            os.makedirs(image_dir_path)

        print(image_file_path)

        headers = {'Referer': episode_url}
        image_file_data = requests.get(image_file_url, headers=headers).content
        print(type(image_file_data))
        print(len(image_file_data))
        open(image_file_path, 'wb').write(image_file_data)
    
    print('Completed !')

if __name__ == '__main__':

    episode_url = 'http://webtoon.daum.net/webtoon/viewer/72779'
    crawl_naver_webtoon(episode_url)
    
    
