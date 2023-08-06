#!/usr/bin/env python

__all__ = ['yesky_download']

import re
import time
from common import *


def yesky_download(url, merge=True):
	html = get_html(url)
	title = r1(r'video_title\s*[:=]\s*["\']([^"\']+)["\']', html)
	title = unescape_html(title).decode('gb2312')
	assert title
	print 'Video title: ', title
	url = r1(r'FLV_URL\s*[:=]\s*[\'"]([^"\']+)[\'"]', html)
	assert url
	print 'Video url: ', url
	return download_urls([url], title, 'flv', total_size=None, merge=merge)

download = yesky_download
download_playlist = playlist_not_supported('yesky')

def main():
	script_main('yesky', yesky_download)

if __name__ == '__main__':
	main()

