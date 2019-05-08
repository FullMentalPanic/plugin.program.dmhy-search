# -*- coding: utf-8 -*-

# import the kodi python modules we are going to use
# see the kodi api docs to find out what functionality each module provides
import xbmc
import xbmcgui
import xbmcaddon
import os
import subprocess
import requests
import re
from bs4 import BeautifulSoup
try:
    from urllib.parse import quote
except ImportError:
    from urllib import pathname2url as quote

addon = xbmcaddon.Addon()
cwd = addon.getAddonInfo('path').decode('utf-8')
#sys.path.append(os.path.join(cwd,'resources', 'lib'))


base_path = "/home/osmc/hdd/download/"
def creat_folder(dir):
    subprocess.call(['mkdir',dir])
    subprocess.call(['sudo','chmod', '-R', '777', dir])

def Add_Torrent(url,abs_path):
    transmission_add_torrent = ["docker","run","-i", "-t","--network","host", "-v","/storage/docker/hdd/downloads:/downloads", "-v", "/storage/docker/spider_log:/spider_log spider1","/usr/bin/transmission-remote", "-n", "transmission:transmission",]
    if not os.path.isdir(abs_path):
        creat_folder(abs_path)
    transmission_add_torrent.append("--add")
    transmission_add_torrent.append(url)
    transmission_add_torrent.append("-w")
    transmission_add_torrent.append(abs_path)
    return subprocess.call(transmission_add_torrent)


class dmhy_rss_search(object):
    domain = "https://share.dmhy.org"
    search_link="https://share.dmhy.org/topics/list?keyword="
    header={
       "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
       "Accept-Encoding":"gzip, deflate",
       "Accept-Language":"zh-CN,zh;q=0.8",
       "Cache-Control":"max-age=0",
       "Connection":"keep-alive",
       "Content-Length":"65",
       "Content-Type":"application/x-www-form-urlencoded",
       "Host":"btkitty.bid",
       "Origin":"blog.aipanpan.com",
       "Referer":"blog.aipanpan.com",
       "Upgrade-Insecure-Requests":"1",
       "User-Agent":"Mozilla/5.0 (Windows NT 10.0.14393; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2950.5 Safari/537.36"
       }
    search_list_info = []
    search_list_magent = []

    dialog = xbmcgui.Dialog()

    def run(self):
        word = self.dialog.input('Enter Key Word for search', type=xbmcgui.INPUT_ALPHANUM)
        if not word:
            return
        self.dialog.notification('dmhy-search', 'Start search...')
        key = quote(word)
        url = self.search_link + key
        self.extract_info(url)
        if self.search_list_info is []:
            self.dialog.notification('dmhy-search', 'No resource find.')
            return
        self.download_task()
        self.dialog.notification('dmhy-search', 'Finished.')

    def extract_info(self,url):
        count = 0
        while count < 2:
            res=requests.get(url)
            bs=BeautifulSoup(res.text,"html.parser")
            result = bs.find_all("div", class_="table clear")
            animate_infos = result[0].find("tbody")
            if animate_infos is None:
                return
            animate = animate_infos.find_all("tr", class_="")
            for link in animate:
                tmp = link.find("td", "title")
                title = (tmp.find("a", target="_blank")).text.strip()
                tmp = link.find_all("td", nowrap="nowrap")
                magent = (tmp[0].a).get('href') #magent
                size = tmp[1].text.strip() #size
                seed = tmp[2].text.strip() # seed
                finished = tmp[3].text.strip() # finished
                info = title + '+'+size+'+'+seed+'+'+finished
                self.search_list_info.append(info)
                self.search_list_magent.append(magent)

            change_page = result[0].find("div", class_= "fl")
            page_links = change_page.find_all("a")
            if len(page_links) < 1:
                return
            if len(page_links) < 2:
                count = count + 1
            next_page = page_links[-1].get('href')
            url = self.domain + next_page

    def download_task(self):
        nums = self.dialog.multiselect("Pls choose download :",self.search_list_info)
        if nums is None:
            return
        folder = self.dialog.input('Enter Folder for download', type=xbmcgui.INPUT_ALPHANUM)
        if not folder:
            abs_path = base_path
        else:
            abs_path = base_path + folder + '/'
        for num in nums:
            Add_Torrent(self.search_list_magent[num], abs_path)
            self.dialog.notification('dmhy-search',self.search_list_info[num])




search = dmhy_rss_search()
search.run()



# the end!
