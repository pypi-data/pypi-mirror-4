#!/usr/bin/env python
# Not support film.qq.com now because they're not free
# 
__all__ = ['qq_download_by_id']

import re
from common import *

def qq_download_by_id(id, title, merge=True):
	# Another method
	# urltemp = 'http://vv.video.qq.com/geturl?vid='+ id + '&otype=xml&platform=1&ran=0%2E9652906153351068'
	# url =  r1(r'''<url>(\w+)</url>''', get_html(urltemp))
	# ref: http://www.zhangweizhong.com/2011/07/qq-video-resources-leak-problem/
    url = 'http://vsrc.store.qq.com/%s.flv' % id
    print 'Video url: ', url
    download_urls([url], title, 'flv', total_size=None, merge=merge)

def qq_download(url, merge=True):
    html = get_html(url, 'utf-8')
    id = r1(r'vid=(\w+)', url)
    if not id:
        id = r1(r'vid\w*:\w*"(\w+)"\w*,', html)
    assert id, "can't find video info"
    title = r1(r'v?id="'+ id + r'" +info="([^"]+)"', html)
    if not title:
        title = r1(r'v?id="'+ id + r'" +title="([^"]+)"', html)
    if not title:
        title = r1(r'title\w*:\w*"([^"]+)"', html)
    assert title, "can't get title"
    title = unescape_html(title)
    print 'Video title: ', title
    return qq_download_by_id(id, title)

download = qq_download
download_playlist = playlist_not_supported('qq')

def main():
    script_main('qq', qq_download)

if __name__ == '__main__':
    main()
