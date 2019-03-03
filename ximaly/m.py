#coding=utf-8
import requests
from bs4 import BeautifulSoup
from pydub import AudioSegment
import sys
import json
import os
import io
import time

# sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf8') 
# 改变标准输出的默认编码

class xmly(object):
    def __init__(self,url,dst):
        self.url = url
        self.dst = dst

    def loadData(self,url,param):
        h = {
            "Host": "www.ximalaya.com",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:64.0) Gecko/20100101 Firefox/64.0",
            "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
            "Accept-Encoding": "gzip, deflate, br"
        }
        #r = requests.request("GET",url,headers=h)
        req = requests.get(url,headers=h,params=param)
        return req

    def Run(self,album):
        if not os.path.exists(self.dst):
            os.makedirs(self.dst)
        page = 1
        data = self.page(album,page)
        while data is not None and len(data["tracksAudioPlay"]) > 0:
            audios = data["tracksAudioPlay"]
            print("Page:",data.get("pageNum",-1),",total:",len(audios))
            self.download(page,audios)
            page += 1
            data = self.page(album,page)     
            #break                 
        return "ok"

    def page(self,album,num):
        url = self.url
        param = {
            "albumId":album,
            "pageNum":num,
            "pageSize":30
        }
        rsp = self.loadData(url,param)
        content = rsp.text.encode('utf-8')
        obj = json.loads(content.decode())
        # check
        status = obj.get("ret",-1)
        if status != 200 :
            print("status:",status)
            return None
        return obj.get("data",None)

    def download(self,page,audios):
        for audio in audios:
            src = audio["src"]
            path = self.dst+"/"+str(audio["index"]) + ".mp3"
            tm1 = time.time()
            rsp = requests.get(src)
            tm2 = time.time()
            reader = io.BytesIO(rsp.content)
            aud = AudioSegment.from_file(reader)
            aud.export(path,format="mp3")
            tm3 = time.time()
            tmf = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) 
            print("  %s Page %d, %s,下载用时:%-.2fs,转码用时:%-.2fs finish"%(page,tmf,path,tm2-tm1,tm3-tm2))
            #break
        tmf = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) 
        print("%s Page %d Finish"%(tmf,page))

if __name__ == "__main__":
    print("sys encode",sys.getdefaultencoding())
    url = 'https://www.ximalaya.com/'
    url = 'https://www.ximalaya.com/xiangsheng/2677356/'
    url = 'https://www.ximalaya.com/revision/play/album'
    #?albumId=2677356&pageNum=1&sort=-1&pageSize=30'
    dst = './downloadx'
    x = xmly(url,dst)
    err = x.Run("2677356")
    print("\n",err)

   