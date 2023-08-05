#!/usr/bin/env python

__all__ = ['zol_download']

import re
import time
from common import *

def zol_download_by_id(vid, title, merge):
	from xml.dom.minidom import parseString
	info_xml=get_html('http://v.zol.com.cn/xmlmaker.php?vid='+vid)
	doc = parseString(info_xml)
	xml=doc.getElementsByTagName('file')[0]
	url=''
	if xml.getAttribute('hd_file_src'):
		url=xml.getAttribute('hd_file_src')
	if not url:
		url=xml.getAttribute('file_src')

	download_urls([url], title, 'flv', total_size=None, merge=merge)

def zol_download(url, merge=True):
	html = get_html(url)
	title = r1(r'title\s*:\s*"([^"]+)"', html)
	title = unescape_html(title).decode('gb2312')
	assert title
	print 'Video title: ', title
	vid = r1(r'vid\s*:\s*"(\d+)"', html)
	assert vid
	return zol_download_by_id(vid, title, merge)

download = zol_download
download_playlist = playlist_not_supported('zol')

def main():
	script_main('zol', zol_download)

if __name__ == '__main__':
	main()



