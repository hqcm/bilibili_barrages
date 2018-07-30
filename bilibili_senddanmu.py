import os
import pickle
import random
import sys
import time

import requests

from bilibili_login import Geetest

#cookie过期问题？
class Send_liveRoll(object):
    def __init__(self):
        self.cookies_dict={}
        cookies_path=r'C:\Users\Administrator\Desktop\bilibili_danmu\cookie.pkl'
        while not os.path.exists(cookies_path):
            geetest=Geetest()
            username='18700780227'
            passwd='13102030032'
            geetest.login(username,passwd)
        with open(cookies_path, 'rb') as f:
            cookies=pickle.load(f)
            #cooikes中用到的只有name及对应的value
            for cookie in cookies:
                self.cookies_dict[cookie['name']] = cookie['value']
        self.roomid='5279'
        self.msg='a test for bilibili'
        #self.cookies_dict1={'Cookie':'l=v; LIVE_BUVID=AUTO3515329180687096; buvid3=44B68F731-75C2-4CCF-998C-0C35FFF0FEC416071infoc; fts=1532918039; sid=d1u3llad; finger=c650951b; Hm_lvt_8a6e55dbd2870f0f5bc9194cddf32a02=1532914195,1532914246,1532914267,1532914296; Hm_lpvt_8a6e55dbd2870f0f5bc9194cddf32a02=1532914441; DedeUserID=25856255; DedeUserID__ckMd5=ce7eb7753764d1fc; SESSDATA=c70acb50%2C1535506178%2C8ebed6c4; bili_jct=b6f94527d084660f7cfe2e1e63e140d8; _dfcaptcha=5f3b809d3ff97cc7e79d553c82caa570'}
        self.url1='https://api.live.bilibili.com/ajax/msg'
        self.url2='https://api.live.bilibili.com/msg/send'
        self.data1={'csrf_token':'',	
                    'roomid': self.roomid,
                    'visit_id':'a9hdtp2fog00'}
        self.data2={'color':'16777215',
                    #csrf_token来自于cookies
                    'csrf_token':self.cookies_dict['bili_jct'],
                    'fontsize':'25',
                    'mode':'1',
                    'msg':self.msg,
                    'rnd':'1532873486',
                    'roomid': self.roomid,
                    }                   
        self.headers={'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'}

    def get_Roll(self):
        '获取弹幕'
        html=requests.post(self.url1,self.data1)
        danmus=list(map(lambda i:html.json()['data']['room'][i]['text'],range(10)))
        self.msg=random.choice(danmus)+'test'

    def send_liveRoll(self):
        '发送弹幕'
        requests.post(self.url2, data=self.data2, cookies=self.cookies_dict, headers=self.headers)
     
if __name__=='__main__':
    send_Rolls=Send_liveRoll()
    for _ in range(2):
        send_Rolls.get_Roll()
        send_Rolls.send_liveRoll()
        time.sleep (random.randint(5,10))
