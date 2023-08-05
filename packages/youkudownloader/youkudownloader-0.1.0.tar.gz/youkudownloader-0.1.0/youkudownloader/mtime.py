#!/usr/bin/env python

__all__ = ['mtime_download']

import re
from common import *

def mtime_download_by_vid(vid, merge):
	import json
	js=json.loads(get_html('http://api.mtime.com/trailer/getvideo.aspx?vid=' + vid))
	title = js['title']
	assert title
	ext='flv'
	if not js.has_key(ext):
		ext='mp4'
	url=js[ext]
	assert url
	download_urls([url], title, ext, total_size=None, merge=merge)

def mtime_download(url, merge=True):
	html = get_html(url)
	vid = r1(r'''vid[:=](\d+)''', html)
	return mtime_download_by_vid(vid, merge)

download = mtime_download
download_playlist = playlist_not_supported('mtime')

def main():
	script_main('mtime', mtime_download)

if __name__ == '__main__':
	main()



