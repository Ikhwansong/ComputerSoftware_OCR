# -*- coding: utf-8 -*-
"""
Created on Thu Jun 11 10:19:22 2020

@author: dlrgh
"""


#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May 24 20:24:12 2020

@author: ihsong
refer site : 

http://pythonstudy.xyz/python/article/404-%ED%8C%8C%EC%9D%B4%EC%8D%AC-Selenium-%EC%82%AC%EC%9A%A9%ED%95%98%EA%B8%B0


"""


import os
import requests
import urllib.request

from selenium import webdriver
options = webdriver.ChromeOptions()
options.add_argument('headless')
browser = webdriver.Chrome('./chromedriver', chrome_options = options)
# options.add_argument('window-size=1920x1080')
# options.add_argument('disable-gpu')


#browser = webdriver.Chrome('./chromedriver')

webtoon_url_list = ['http://webtoon.daum.net/webtoon/viewer/72780', 'http://webtoon.daum.net/webtoon/viewer/72782', 'http://webtoon.daum.net/webtoon/viewer/72783',
                    'http://webtoon.daum.net/webtoon/viewer/72784', 'http://webtoon.daum.net/webtoon/viewer/73420', 'http://webtoon.daum.net/webtoon/viewer/74000',
                    'http://webtoon.daum.net/webtoon/viewer/74487' ]

for webtoon_url in webtoon_url_list :  

    browser.implicitly_wait(20)
    browser.get(webtoon_url)
    browser.implicitly_wait(20)
    comic_title = browser.find_element_by_css_selector('a.link_title').text
    comic_title = 'the_world_of_dog'
    episode_num = browser.find_element_by_class_name('txt_episode').text
    episode_num = 'ep' + episode_num[:-1]
    imgs = browser.find_elements_by_class_name('img_webtoon')
    
    
    image_file_url =''
    for num,i in enumerate(imgs):        
        image_file_url = i.get_attribute('src')
        image_dir_path = os.path.join(os.path.dirname(__file__), comic_title, episode_num)
        image_file_path = os.path.join(image_dir_path, os.path.basename(image_file_url))
    
        if not os.path.exists(image_dir_path):
            os.makedirs(image_dir_path)
        headers = {'Referer': webtoon_url}
        
        #image_file_data = requests.get(image_file_url, headers=headers).content
        #open(image_file_path, 'wb').write(image_file_data)
        #os.rename(image_file_path, os.path.join('\\'.join(image_file_path.split('\\')[:-1]) , str(num) + '.jpeg'))
        urllib.request.urlretrieve(image_file_url, os.path.join('\\'.join(image_file_path.split('\\')[:-1]) , str(num) + '.png') )
        
    print('complete!')
browser.quit()
