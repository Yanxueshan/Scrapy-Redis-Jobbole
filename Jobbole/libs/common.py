'''
    本模块用于编写一些用于Scrapy中的一些可用函数
'''

import hashlib


def get_md5(url):
    '''
        将url进行md5哈希，返回固定长度的字符串
    '''
    if isinstance(url, str):
        url = url.encode('utf-8')
    return hashlib.md5(url).hexdigest()
