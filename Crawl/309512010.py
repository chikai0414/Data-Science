# -*- coding:utf-8 -*
from collections import OrderedDict
from operator import getitem
import re
import argparse
import sys
from argparse import ArgumentParser
import requests
from bs4 import BeautifulSoup
import time


headers = {
    'User-Agent': 'Mozilla/5.0 \
        (Macintosh; Intel Mac OS X 10_13_4) \ AppleWebKit/537.36 (KHTML, like Gecko) \ Chrome/35.0.1916.47 Safari/537.36'}

def decode(cfemail):
    enc = bytes.fromhex(cfemail)
    return bytes([c ^ enc[0] for c in enc[1:]]).decode('utf8')

def deobfuscate_cf_email(soup):
    for encrypted_email in soup.select('span.__cf_email__'):
        #print(encrypted_email['data-cfemail'])
        decrypted = decode(encrypted_email['data-cfemail'])
        encrypted_email.replace_with(decrypted)
def extract_content(kw, url, img_url):
    r = requests.get(url, headers=headers, cookies={'over18': '1'})
    time.sleep(0.01)
    content = r.text.encode('utf-8')
    soup = BeautifulSoup(content, 'html.parser')
    main = soup.find(id='main-content').text
    patt = '發信站'
    starting = re.search(patt, main)
    if starting is None:
        return
    search_area = main.split('\n')
    for line in search_area:
        if re.search(patt, line) is not None:
            break
        else:
            if re.search(kw, line) is not None:
                #print('match', url)
                get_img_url(url, img_url)
                break


def keyword(kw, start, end):
    start_time = time.time()
    key_txt = open('keyword(%s)[%d-%d].txt' % (kw, start, end), 'w+',encoding='utf-8')
    all_art = open('all_articles.txt', 'r',encoding='utf-8')
    art = all_art.readlines()
    all_art.close()

    for data in art:
        t = data.split(',')
        url = t[-1].rstrip()
        if int(t[0]) > end:
            break
        if int(t[0]) >= start:
            img_url = []
            extract_content(kw,url,img_url)
            key_txt.writelines(img_url)

    key_txt.close()
    print('finish in : ' + str(time.time() - start_time))

def  crawl(url):
    all_art = open('all_articles.txt', 'wb+')
    pop_art = open('all_popular.txt', 'wb+')
    start_time = time.time()
    month_count = 1
    save = False
    start= False
    done = False

    while not done:
        time.sleep(0.01)
        r = requests.get(url, headers=headers, cookies={'over18': '1'})
        content = r.text.encode('utf-8')
        soup = BeautifulSoup(content, "html.parser")

        ent = soup.find_all(class_='r-ent')
        for e in ent :
            date = e.find_all(class_='date')
            t = date[0].string.split('/')
            day = int(t[0] + t[-1])
            month = day//100
            if start == False and month == 12 :
                save = False
                continue
            elif  start == False and month == 1 :
                start = True
                save =True
            if start == True and month_count != month :
                month_count+=1
                if month_count == 13 :
                    done = True 
                    save = False
            else : 
                save = True

            if save:
                l = e.find_next('a')
                deobfuscate_cf_email(l)
                url = 'https://www.ptt.cc' + l.get('href')
                title = list(l.strings)
                nrecs = e.find_all('span')
                nrec = ''
                if len(nrecs) != 0:
                    nrec = nrecs[0].string
                info = str(day)+','+''.join(title)+','+url+'\n'
                if re.search("公告", info) is not None:
                    continue
                all_art.write(info.encode('utf-8'))
                if nrec == '爆':
                    pop_art.write(info.encode('utf-8'))
        url = "https://www.ptt.cc" + soup.find_all(class_='btn wide')[2].get('href')
    print('finish in : ' + str(time.time() - start_time))
    all_art.close()
    pop_art.close()

def  push(start,end):
    start_time = time.time()
    all_art = open('all_articles.txt','r',encoding='utf-8')
    art = all_art.readlines()
    all_art.close()
    push_sh_data={}
    for data in art:
        t = data.split(',')
        url = t[-1].rstrip()
        if int(t[0]) > end :
            break
        if int(t[0]) >= start :
            r = requests.get(url, headers=headers, cookies={'over18': '1'})
            time.sleep(0.01)
            content = r.text.encode('utf-8')
            soup = BeautifulSoup(content, 'html.parser')
            for push in soup.find_all(class_='push'):
                p = push.find_all('span')
                tag = p[0].string
                user = p[1].string
                if user not in push_sh_data :
                    push_sh_data[user] = {'push': 0, 'sh': 0}
                
                if tag == "推 ":
                    push_sh_data[user]['push'] += 1
                elif tag == "噓 ":
                    push_sh_data[user]['sh'] += 1
    push_num = 0
    sh_num = 0
    for user, item in push_sh_data.items():
        push_num += item['push']
        sh_num += item['sh']  
    text = []
    #print('all push:', push_num)
    #print('all sh:', sh_num)
    text.append('all like: %d\nall boo: %d\n' %(push_num,sh_num))

    push_sort = sorted(push_sh_data, key=lambda x: (
        push_sh_data[x]['push']*-1, x))
    sh_sort = sorted(push_sh_data, key=lambda x: (
        push_sh_data[x]['sh']*-1, x))

    for i in range(10):
        print(push_sort[i],push_sh_data[push_sort[i]]['push'])
        text.append('like #%d: %s %d\n' %(i+1,push_sort[i],push_sh_data[push_sort[i]]['push']))
    for i in range(10):
        print(sh_sort[i],push_sh_data[sh_sort[i]]['sh'])
        text.append('boo #%d: %s %d\n' %(i+1,sh_sort[i],push_sh_data[sh_sort[i]]['sh']))

    txt = open('push[%d-%d].txt' %(start, end), 'w+')
    txt.writelines(text)
    txt.close()
    print('finish: '+ str(time.time() - start_time))

def get_img_url(url, data):
    r = requests.get(url, headers=headers, cookies={'over18': '1'})
    time.sleep(0.01)
    content = r.text.encode('utf-8')
    soup = BeautifulSoup(content, 'html.parser')
    patt = 'href="(http)(.*)?(jpg|jpeg|png|gif)'
    img_url = re.findall(patt, soup.prettify())
    for s in img_url:
        data.append(''.join(s)+'\n')


def popular(start, end):
    start_time = time.time()
    pop_art = open('all_popular.txt', 'r',encoding='utf-8')
    pop_txt = open('popular[%d-%d].txt' % (start, end), 'w+')
    art = pop_art.readlines()
    pop_art.close()
    art_url = []
    for data in art:
        t = data.split(',')
        url = t[-1].rstrip()
        if int(t[0]) > end :
            break
        if int(t[0]) >= start :
            art_url.append(url)
    num = len(art_url)
    pop_txt.write("number of popular articles: %d\n" % num)
    img_url = []
    for url in art_url:
        get_img_url(url, img_url)
        pop_txt.writelines(img_url)

    pop_txt.close()
    print('finish: '+ str(time.time() - start_time))


if __name__ == "__main__":
    url = "https://www.ptt.cc/bbs/Beauty/index2748.html"
    #crawl(url)
    #push(101,101)
   # popular(101,201)
    parser = ArgumentParser()
    parser.add_argument('pos',type=str,nargs='+')
    args = parser.parse_args()

    if args.pos[0] == 'crawl' :
            crawl(url)
    elif args.pos[0] == 'push':
            push(int(args.pos[1]),int(args.pos[2]))
    elif args.pos[0] == 'popular':
            popular(int(args.pos[1]),int(args.pos[2]))
    elif args.pos[0] == 'keyword':
            keyword(args.pos[1],int(args.pos[2]),int(args.pos[3]))

