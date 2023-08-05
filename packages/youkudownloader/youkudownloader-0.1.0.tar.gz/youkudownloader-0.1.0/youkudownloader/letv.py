#!/usr/bin/env python

__all__ = ['letv_download', 'letv_download_playlist', 'letv_download_by_vid']

from common import *

def letv_download_by_vid(vid, title, merge=True):
	xml = get_html('http://app.letv.com/v.php?id=' + vid )

	from xml.dom.minidom import parseString
	doc = parseString(xml)
	title = title or doc.firstChild.getAttribute('tal') 
	url1 = r1(r'url\s*"\s*[:=]\s*"([^"]+)"', xml).replace('\\','')

	# visit url1 to find real urls
	xml = get_html(url1)
	url = r1(r'location\s*"\s*[:=]\s*"([^"]+)"', xml).replace('\\','')
	assert 'flv' in url

	download_urls([url], title, 'flv', total_size=None, merge=merge)

def letv_download(url, merge=True):
	html = get_decoded_html(url)
	vid = r1(r'[xv]id\s*[:=]\s*(\d+)', html)
	assert vid
	title = r1(r'''title\s*[:=]\s*['"]([^"]+)['"]\s*,''', html)
	if r1(r'''html" target="_blank"\>\[([^"]+)\]''', html):
		title=r1(r'''html" target="_blank"\>\[([^"]+)\]''', html)
	assert title
	title = unescape_html(title)
	letv_download_by_vid(vid, title, merge=merge)

def parse_playlist(url):
	raise NotImplementedError(url)

def letv_download_playlist(url, create_dir=False, merge=True):
	if create_dir:
		raise NotImplementedError('please report a bug so I can implement this')
	videos = parse_playlist(url)
	for i, (title, id) in enumerate(videos):
		print 'Downloading %s of %s videos...' % (i + 1, len(videos))
		letv_download_by_vid(id, title, merge=merge)

download = letv_download
download_playlist = letv_download_playlist

def main():
	script_main('letv', letv_download, letv_download_playlist)

if __name__ == '__main__':
	main()

