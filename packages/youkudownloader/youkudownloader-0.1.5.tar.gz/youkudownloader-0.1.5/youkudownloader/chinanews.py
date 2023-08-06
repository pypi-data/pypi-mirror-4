#!/usr/bin/env python

__all__ = ['chinanews_download']

import re
import time
from common import *


def chinanews_download(url, merge=True):
	html = get_decoded_html(url)
	title = r1(r'''newstitle\s*[:=]\s*["']([^'"]+)['"]''', html)
	if not title:
		title = r1(r'''newstitle" +type="hidden" +value=['"]([^'"]+)['"]''', html)
	title = unescape_html(title).decode('gb2312')
	assert title
	url = r1(r'vInfo=([^\'"]+)\.mp4', html)+ '.mp4'
	assert url
	print 'Videos title', title
	print 'Videos url:', url
	download_urls([url], title, 'mp4', total_size=None, merge=merge)

download = chinanews_download
download_playlist = playlist_not_supported('chinanews')

def main():
	script_main('chinanews', chinanews_download)

if __name__ == '__main__':
	main()



