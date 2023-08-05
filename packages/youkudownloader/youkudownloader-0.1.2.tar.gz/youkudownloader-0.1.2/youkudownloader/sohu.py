#!/usr/bin/env python

__all__ = ['sohu_download']
import time
from common import *

def real_url(host, prot, file, new):
	tries = 3
	url = 'http://%s/?prot=%s&file=%s&new=%s' % (host, prot, file, new)
	print 'Temp video url: ', url
	start = ''
	key = ''
	while tries > 0:
		try:
			start, _, host, key, _, _ = get_html(url).split('|')
			return '%s%s?key=%s' % (start[:-1], new, key)
		except:
			tries =  tries -1
			continue
	return ''
		

def sohu_download(url, merge=True):
	vid = r1('vid[:=]\s*[\'"](\d+)[\'"]', get_html(url))
	assert vid
	import json
	try:
		jsdata = get_decoded_html('http://hot.vrs.sohu.com/vrs_flash.action?vid=%s' % vid)
	except:
		jsdata = get_decoded_html('http://my.tv.sohu.com/videinfo.jhtml?m=viewtv&vid=%s' % vid)

	data = json.loads(jsdata)
	host = data['allot']
	prot = data['prot']
	urls = []
	data = data['data']
	title = data['tvName']
	size = sum([int(x) for x in data['clipsBytes']])
	assert len(data['clipsURL']) == len(data['clipsBytes']) == len(data['su'])
	for file, new in zip(data['clipsURL'], data['su']):
		urls.append(real_url(host, prot, file, new))
	assert data['clipsURL'][0].endswith('.mp4')
	print "Video URLs: ", urls
	download_urls(urls, title, 'mp4', total_size=size, refer=url, merge=merge)

download = sohu_download
download_playlist = playlist_not_supported('sohu')

def main():
	script_main('sohu', sohu_download)

if __name__ == '__main__':
	main()

