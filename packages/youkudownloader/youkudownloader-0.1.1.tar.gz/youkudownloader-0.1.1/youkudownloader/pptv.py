#!/usr/bin/env python
# TODO: can't download now

__all__ = ['pptv_download', 'pptv_download_by_id']

import re
import urllib
from common import *
import hashlib
import time

def pptv_download_by_id(id, merge=True):
	xml = get_html('http://web-play.pptv.com/webplay3-0-%s.xml' % id)
	#xml = xml.decode('utf-8')
	host = r1(r'<sh>([^<>]+)</sh>', xml)
	st = r1(r'<st>([^<>]+)</st>', xml)
	t=(time.mktime(time.strptime(st.replace(' UTC',''))) - 60*1000)/1000 
	ts=time.strftime('%a %b %d %Y %H:%M:%S UTC', time.localtime(t))
	key = hashlib.md5(str(t)).hexdigest() # FIXME: incorrect key
	rids = re.findall(r'rid="([^"]+)"', xml)
	rid = r1(r'rid="([^"]+)"', xml)
	title = r1(r'nm="([^"]+)"', xml)
	assert title
	print 'Video title: ', title
	pieces = re.findall('<sgm no="(\d+)"[^fs]*fs="(\d+)"', xml)
	numbers, fs = zip(*pieces)
	urls = ['http://%s/%s/%s?key=%s' % (host, i, rid, key) for i in numbers]
	#urls = ['http://pptv.vod.lxdns.com/%s/%s?key=%s' % (i, rid, key) for i in numbers]
	total_size = sum(map(int, fs))
	assert rid.endswith('.mp4')
	print 'Video url: ', urls
	download_urls(urls, title, 'mp4', total_size=total_size, merge=merge)

def pptv_download(url, merge=True):
	html = get_html(url)
	id = r1(r'webcfg\s*=\s*{"id":\s*(\d+)', html)	# http://v.pptv.com/show/65zSUKG0Kmh0vySKibg.html
	if not id:
		id_str=r1(r'var allList = \[(["\',\d]+)\]', html)	# 8.pptv.com/series/zhaojiaban/
		ids = re.findall(r'"(\d+)"', id_str)
		for id in ids:
			pptv_download_by_id(id, merge=merge)
	else:
		pptv_download_by_id(id, merge=merge)

download = pptv_download
download_playlist = playlist_not_supported('pptv')

def main():
	script_main('pptv', pptv_download)

if __name__ == '__main__':
	main()

