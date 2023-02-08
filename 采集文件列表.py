import requests
import json
import threading
import re
import time


class Get_list:
    '''采集文件列表'''

    result: list
    '''采集结果'''

    def __init__(self):
        self.lock = threading.Lock()
        self.sem = threading.Semaphore(20)
        text = text = open('数据源/校验成功数据源.txt', 'r').read()
        data = text.split('\n')
        threads = []
        self.result = []
        for i in data:
            data = i.split('|')
            url = data[0]
            password = data[1] if len(data) > 1 else None
            self.sem.acquire()
            thread = threading.Thread(target=self.get_list, args=(url, password))
            thread.start()
            threads.append(thread)
        for i in threads:
            i.join()
        filename = '采集结果 - ' + str(int(time.time())) + '.txt'
        json.dump(self.result, open(filename, 'w', encoding='utf-8'))

    def get_list(self, url: str, password: str):
        def get_page(config: dict):
            url = 'https://www.lanzoui.com/filemoreajax.php'
            r = requests.post(
                url,
                data=config,
                headers={'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'},
            )
            r.encoding = 'utf-8'
            if type(json.loads(r.text)['text']) is not list:
                return
            for i in json.loads(r.text)['text']:
                m = re.match(r'^(\d+)\s*天前', i['time'])
                if m:
                    day = int(m.group(1))
                elif i['time'].startswith('昨天'):
                    day = 1
                elif i['time'].startswith('前天'):
                    day = 2
                elif i['time'].endswith('小时前'):
                    day = 0
                elif i['time'].endswith('分钟前'):
                    day = 0
                elif i['time'].endswith('秒前'):
                    day = 0
                else:
                    day = -1
                if day > -1:
                    i['time'] = time.strftime(
                        '%Y-%m-%d', time.localtime(time.time() - day * 24 * 60 * 60)
                    )
                self.lock.acquire()
                self.result.append(i)
                self.lock.release()
            return True

        config: dict = self.get_config(url, password)
        if not config:
            self.lock.acquire()
            print(url)
            self.lock.release()
        # page = 0
        # while True:
        #     page += 1
        #     config['pg'] = page
        #     if not get_page(config):
        #         break
        #     time.sleep(1)
        # title = config['title']
        # self.lock.acquire()
        # print(title + ' - 采集完成')
        # self.lock.release()
        # self.sem.release()

    def get_config(self, url: str, password: str) -> dict:
        '''获取配置信息'''
        r = requests.get(
            url, headers={'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )
        r.encoding = 'utf-8'
        html = r.text
        if not html:
            self.lock.acquire()
            print('重试中')
            self.lock.acquire()
            return self.get_config(url, password)
        elif html.find('filemoreajax') == -1:
            return
        folds = re.findall(r'<div class="mbx mbxfolder">.*?<a href="(.*?)"', html)
        for fold in folds:
            threading.Thread(
                target=self.get_list, args=('https://www.lanzoui.com' + fold, password)
            ).start()
        title = re.findall(r'<title>(.*?)</title>', html)[0]
        uid = re.search(r'\'uid\'\s*:\s*\'(.*?)\'', html)
        uid = uid.group(1) if uid else ''
        lx = re.search(r'\'lx\'\s*:\s*(.*?),', html)
        lx = lx.group(1) if lx else ''
        fid = re.search(r'\'fid\'\s*:\s*(.*?),', html)
        fid = fid.group(1) if fid else ''
        rep = re.search(r'\'rep\'\s*:\s*(.*?),', html)
        rep = rep.group(1) if rep else ''
        up = re.search(r'\'up\'\s*:\s*(.*?),', html)
        up = up.group(1) if up else ''
        ls = re.search(r'\'ls\'\s*:\s*(.*?),', html)
        ls = ls.group(1) if ls else ''
        t = re.search(r'\'t\'\s*:\s*(.*?),', html)
        t = t.group(1) if t else ''
        k = re.search(r'\'k\'\s*:\s*(.*?),', html)
        k = k.group(1) if k else ''
        t = re.search(r'var\s*' + t + '\s*=\s*\'(.*?)\'', html)
        t = t.group(1) if t else ''
        k = re.search(r'var\s*' + k + '\s*=\s*\'(.*?)\'', html)
        k = k.group(1) if k else ''
        return {
            'lx': lx,
            'fid': fid,
            'uid': uid,
            'rep': rep,
            't': t,
            'k': k,
            'up': up,
            'ls': ls,
            'pwd': password,
            'title': title,
        }


Get_list()
