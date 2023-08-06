#!/usr/bin/env python

__all__ = ['ku6_download', 'ku6_download_by_id']

import json
import re
from common import *

def ku6_download_by_id(id, title=None, output_dir='.', merge=True):
	# data = json.loads(get_html('http://v.ku6.com/fetchVideo4Player/%s...html'%id))['data']
	# refer to http://dev.ku6.com/?q=node/17
	data = json.loads(get_html('http://v.ku6.com/fetch.htm?t=getVideo4Player&vid=%s...'%id))['data']
	t = data['t']
	f = data['f']
	title = title or t
	assert title
	urls = f.split(',')
	#if len(urls) == 1:
	#	size = int(re.search(r'\d+$',str(data['videosize'])).group(0))*0.38
	#else:
	#	size = int(re.search(r'\d+$',str(data['videosize'])).group(0))*0.22
	size = float(re.search(r'\d+$',str(data['videosize'])).group(0))
	ext = re.sub(r'.*\.', '', urls[0])
	assert ext in ('flv', 'mp4', 'f4v'), ext
	ext = {'f4v':'flv'}.get(ext, ext)
	download_urls(urls, title, ext, total_size=size, merge=merge)

def ku6_download(url, merge=True):
	patterns = [r'http://v.ku6.com/special/show_\d+/(.*)\.\.\.html',
                    r'http://v.ku6.com/show/(.*)\.\.\.html',
                    r'http://my.ku6.com/watch\?.*v=(.*)\.\..*']
	ids = r1_of(patterns, url)
	ku6_download_by_id(ids, merge=merge)

download = ku6_download
download_playlist = playlist_not_supported('ku6')

def main():
	script_main('ku6', ku6_download)

if __name__ == '__main__':
	main()

