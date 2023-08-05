#!/usr/bin/env python

__all__ = ['iqiyi_download']

import re
import time
from common import *

def real_url(url): 
	url=url.replace('.f4v', '.mp4')
	url2=''
	for i in range(3):
		html=get_html(url)
		try:
			url2=r1(r'"l":"([^"]+)"',html).replace('.mp4', '.f4v')
			size=urls_size(url2)
			if size > 0:
				break
		except:
			#print 'Invalid URL: ', url2
			time.sleep(0.1)
			continue
	return url2

def real_url2(url): 
	return url.replace('http://data.video.qiyi.com/videos', 'http://wgdcdn.inter.qiyi.com/videos2')

def iqiyi_download(url, merge=True):
	html = get_html(url)
	#title = r1(r'title\s*:\s*"([^"]+)"', html)
	#title = unescape_html(title).decode('utf-8')
	videoId = r1(r'''videoId["']?\s*[:=]\s*["']([^"']+)["']''', html)
	print 'Get videoId: ', videoId
	assert videoId
	info_url = 'http://cache.video.qiyi.com/v/%s' % videoId
	info_xml = get_html(info_url)

	from xml.dom.minidom import parseString
	doc = parseString(info_xml)
	title = doc.getElementsByTagName('title')[0].firstChild.nodeValue
	size = int(doc.getElementsByTagName('totalBytes')[0].firstChild.nodeValue)
	urls = [n.firstChild.nodeValue for n in doc.getElementsByTagName('file')]
	assert urls[0].endswith('.f4v'), urls[0]
	urls = map(real_url, urls)
	print 'Videos url:', urls
	download_urls(urls, title, 'flv', total_size=size, merge=merge)

download = iqiyi_download
download_playlist = playlist_not_supported('iqiyi')

def main():
	script_main('iqiyi', iqiyi_download)

if __name__ == '__main__':
	main()



