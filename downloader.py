#!/usr/bin/python
import re
import urllib2  
import os
import csv
from bs4 import BeautifulSoup
import string
import cgi

page=1
link='https://yts.lt/browse-movies?page='
download_pref_order = ['1080p.BluRay','1080p.WEB','720p.BluRay','720p.WEB']


def open_link(page_link):
    soup = ''
    request = urllib2.Request(page_link, headers={ 'User-Agent': 'Mozilla/5.0' })
    try:
        response = urllib2.urlopen(request).read()
        soup = BeautifulSoup(response,"html.parser")
    except:
        pass

    return soup

def download_file(url,save_path):
    request = urllib2.Request(url, headers={ 'User-Agent': 'Mozilla/5.0' })
    filename = url.split("/")[-1]
    
    try:
        response = urllib2.urlopen(request)
        header=response.info()['Content-disposition']
        value, params = cgi.parse_header(header)
        filename=params['filename']

    except:
        pass       
    
    data = response.read()

    with open(save_path + '/' + filename, 'wb') as f:
        f.write(data)
    f.close()


def extract_links(soup):
    print '#' + '-'*50 + '#'
    count = 1
    link = soup.findAll('a', {'class' : 'browse-movie-title'})
    for i in link:
        extract_torrent_links(i.get('href'))

def setup_directory(dirName):
    if not os.path.exists(dirName):
        os.mkdir(dirName)

def save_as_csv(path,csvString):
    with open(path+'/description.csv','wb') as f:
        writer = csv.writer(f,delimiter =',',quotechar ='"',quoting=csv.QUOTE_ALL)
        writer.writerow(['title','year','genre','synopsis','directors','actors'])
        writer.writerows(csvString)
    f.close()


def extract_torrent_links(page_link):
    print 'extracting link: ' + page_link,
    soup = open_link(page_link)
    
    if soup == "":
        print " [ERROR]"
        return

    movie_desc = []
    
    #get the movie title
    htmldata = soup.find('div', {'id' : 'mobile-movie-info'})
    movie_desc.append(htmldata.find('h1').text)
    movie_title = htmldata.find('h1').text

    #movie year and genre
    res = [i.text for i in htmldata.findAll('h2')]
    movie_desc.append(res[0])
    movie_desc.append(res[1])
    movie_year = res[0]


    #movie synopsis
    htmldata = soup.find('div', {'id' : 'synopsis'}) 
    movie_desc.append(string.strip(htmldata.find('p', {'class' : 'hidden-xs'}).text))
    
    #directors
    htmldata = soup.find('div', {'class' : 'directors'})
    htmldata = htmldata.findAll('div', {'class' : 'list-cast-info tableCell'})
    try:
        res = [i.find('span',{'itemprop' : 'name'}).text for i in htmldata]
        res = ','.join(map(str,res))
    except:
        res=''

    movie_desc.append(res)

    #actors
    htmldata = soup.find('div', {'class' : 'actors'})
    htmldata = htmldata.findAll('div', {'class' : 'list-cast-info tableCell'})
    try:
        res = [i.find('span',{'itemprop' : 'name'}).text for i in htmldata]
        res = u','.join(map(str,res)).encode('utf-8').strip()
    except:
        res=''
    movie_desc.append(res)

    #get the torrent link
    htmldata = soup.find('p', {'class' : 'hidden-xs hidden-sm'}).findAll('a')
    ilink = ''
    for i in  download_pref_order:
        for j in htmldata:
            if j.text == i:
                ilink = j
                break
        if ilink != '':
            break

    torrent_link = ilink.get('href')

    #movie poster
    htmldata = soup.find('div', {'id' : 'movie-poster'})
    movie_poster = htmldata.find('img').get('src')

    #setup everyting
    setup_directory(movie_year)
    
    movie_path= movie_year + '/' + re.sub('[^a-zA-Z0-9 \n\.]', '', movie_title).replace(" ","_")
    setup_directory(movie_path)

    save_as_csv(movie_path,[movie_desc])
    
    download_file(movie_poster,movie_path)
    download_file(torrent_link,movie_path)
    
    #print torrent_link
    #print [movie_desc]
    #print movie_poster
    print ' [DONE]'



#extract_torrent_links('https://yts.lt/movie/new-tale-of-zatoichi-1963')

while page < 2:
    url = str(link) + str(page)
    soup = open_link(url)
    extract_links(soup)
    print "%s pages done"%str(page)
    page = page + 1
   
