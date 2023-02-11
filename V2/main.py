import requests
import json
import threading
import re
import time
import datetime
import zipfile


class Config:
    '''配置信息'''

    lanzou_domain = 'www.lanzoui.com'
    '''蓝奏云域名'''
    semlock = 30
    '''最大线程数量'''
    source_path = 'source.txt'
    '''数据源文件路径'''
    headers = {'User-Agent': 'apee'}
    '''公共请求头'''


class Check_url:
    '''数据源校验'''

    def __init__(self):
        self.lock = threading.Lock()
        self.semlock = threading.BoundedSemaphore(Config.semlock)
        self.source = self.get_source_list()

    def start(self):
        threads = []
        self.has_check_count = 0  # 已经校验的数量
        self.success_source = []  # 校验成功的数据源
        for i in self.source:
            self.semlock.acquire()
            thread = threading.Thread(target=self.check_source, args=(i,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()
        print('\n校验完成，通过 %d/%d' % (len(self.success_source), len(self.source)))
        return self

    def get_url(self, data: dict) -> str:
        '''从数据源对象中获取 URL'''
        url = 'http://' + Config.lanzou_domain + data['path']
        return url

    def check_source(self, data: dict):
        '''校验一个数据源'''
        url = self.get_url(data)
        '''校验 URL 是否有效'''
        try:
            r = requests.get(url, headers=Config.headers)
            r.encoding = 'utf-8'
        except:
            return self.check_source(data)  # 请求失败，重试
        html = r.text
        if not html:
            return self.check_source(data)  # 空响应，重试
        self.lock.acquire()
        if html.find('filemoreajax') > -1:
            self.has_check_count += 1
            print('\r已校验 %d 条数据源' % (self.has_check_count,), end='')
            self.success_source.append(data)
        else:
            print(url)
        self.lock.release()
        self.semlock.release()

    def get_source_list(self) -> list:
        '''获取数据源 URL 列表'''
        try:
            text = open(Config.source_path, 'r', encoding='utf-8').read()
        except:
            print(Config.source_path + ' 读取失败')
            return
        data = text.split('\n')
        source = []
        for line in data:
            result = re.search(r'^(https?:\/\/[^/]+(.*?))(\|(.*?))?$', line)
            if not result:
                continue  # 当前行没有发现数据源
            path = result.group(2)
            password = result.group(4)
            item = {'path': path, 'pass': password}
            source.append(item)
        return source


class Collect:
    '''文件列表采集'''

    pass


print(Check_url().start().success_source)
