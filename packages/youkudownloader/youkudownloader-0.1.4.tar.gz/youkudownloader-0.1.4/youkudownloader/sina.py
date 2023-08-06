#!/usr/bin/env python

__all__ = ['sina_download', 'sina_download_playlist', 'sina_download_by_vid']

from common import *

def sina_download_by_vid(vid, title, merge=True):
	xml = get_html('http://v.iask.com/v_play.php?vid=' + vid )

	from xml.dom.minidom import parseString
	doc = parseString(xml)
	title = title or unescape_html(doc.getElementsByTagName('vname')[0].firstChild.data)
	assert title
	url=doc.getElementsByTagName('url')[0].firstChild.data
	download_urls([url], title, 'flv', total_size=None, merge=merge)

def sina_download(url, merge=True):
	html = get_decoded_html(url)
	vid = r1(r'''vid\s*[:=]\s*['"](\d+)['"]\s*,''', html)
	assert vid
	sina_download_by_vid(vid, None, merge=merge)

def parse_playlist(url):
	raise NotImplementedError(url)

def sina_download_playlist(url, create_dir=False, merge=True):
	raise NotImplementedError(url)

download = sina_download
download_playlist = sina_download_playlist

def main():
	script_main('sina', sina_download, sina_download_playlist)

if __name__ == '__main__':
	main()

