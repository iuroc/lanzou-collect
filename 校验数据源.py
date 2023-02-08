import requests
import threading
import os


class Check:
    '''校验 URL'''

    result: list
    '''校验成功列表'''
    error: list
    '''校验失败列表'''
    finish_count: int
    '''任务完成数量'''
    all_count: int
    '''任务总数量'''
    line_list: list
    '''数据源按行分隔'''

    def __init__(self):
        self.lock = threading.Lock()
        self.sem = threading.Semaphore(20)
        self.result = []
        self.error = []
        text = open('数据源/未校验数据源.txt', 'r').read()
        self.line_list = text.split('\n')
        self.finish_count = 0
        self.all_count = len(self.line_list)

    def start(self):
        if not os.path.exists('采集结果'):
            os.mkdir('采集结果')
        threads = []
        for i in self.line_list:
            self.sem.acquire()
            thread = threading.Thread(target=self.check_line, args=(i,))
            thread.start()
            threads.append(thread)
        for i in threads:
            i.join()
        self.result = list(set(self.result))
        open('数据源/校验成功数据源.txt', 'w', encoding='utf-8').write('\n'.join(self.result))
        open('数据源/校验失败数据源.txt', 'w', encoding='utf-8').write('\n'.join(self.error))
        print('\r成功 %d 个，失败 %d 个' % (len(self.result), len(self.error)))

    def check_line(self, line: str):
        '''校验 URL'''
        url = line.split('|')[0]
        if not url:
            self.sem.release()
            return
        try:
            r = requests.get(
                url, headers={'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            )
            r.encoding = 'utf-8'
        except:
            return self.check_line(url)
        self.lock.acquire()
        if r.text.find('filemoreajax') != -1:
            self.result.append(line)
        elif not r.text:
            self.lock.release()
            return self.check_line(line)
        else:
            self.error.append(line)
        self.finish_count += 1
        print('\r已校验 %d/%d' % (self.finish_count, self.all_count), end='')
        self.lock.release()
        self.sem.release()


if __name__ == '__main__':
    Check().start()
