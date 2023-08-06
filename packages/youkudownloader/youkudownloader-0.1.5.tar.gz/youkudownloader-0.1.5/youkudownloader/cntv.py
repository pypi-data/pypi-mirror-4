#!/usr/bin/env python

__all__ = ['cntv_download', 'cntv_download_by_id']

from common import *
import json
import re

def get3ByteNumberString(param1):
    if param1 < 10:
        return "00"+str(param1)
    if param1 < 100:
        return "0"+str(param1)
    if param1 < 1000:
        return ""+str(param1)
    return '000'

def xiyou_parser(param1, param2):
    XBK_FLV = "xbk_flv"
    CCTV    = "cctv"
    XBK_MP4 = "xbk_mp4"
    XIYOU   = "xiyou"
    
    if param2 == "true":
        param2 = CCTV
    elif param2 == "xbk_flv":
        param2 = XBK_FLV
    elif param2 == "xbk_mp4":
        param2 = XBK_MP4
    else:
        param2 = XIYOU
    
    _loc_8=''
    _loc_9=''
    _loc_10=''
    _loc_3=''
    _loc_4 = param1.split("#")
    if len( _loc_4)!=2:
        return param1
    _loc_5 = _loc_4[0]
    _loc_6 = _loc_4[1].split('_')
    if len(_loc_6) == 1 and param2 != XIYOU:
        if param2 == CCTV or param2 ==XBK_MP4:
            _loc_3 = _loc_5 + ".mp4"
        elif param2 ==XBK_FLV:
            _loc_3 = _loc_5 + ".flv"
        return _loc_3
    _loc_7=0
    while _loc_7 < len(_loc_6):
        if param2 == CCTV:
            _loc_3 = _loc_5 + "-" + str(_loc_7 + 1) + ".mp4"
        else:
            _loc_3 = _loc_5 + "_" + get3ByteNumberString(_loc_7 + 1) + ".mp4"
        _loc_7 = _loc_7 + 1
    return _loc_3


def cntv_download_by_id(id, title=None, output_dir='.', merge=True, xiyou=False):
	assert id
        title = ''
        urls=[]
        ext=''

        if xiyou:
            info = json.loads(get_html('http://xiyou.cntv.cn/interface/index?videoId='+id).decode('utf-8'))
            isCCTV=info['data'][0]['isCCTV']
            for url in info['data']:
                title = title or url['title']
                videolists= url['videoList']
                for video in videolists:
                    if 'videoFilePathHD' in video:
                        urls.append(xiyou_parser(video['videoFilePathHD'], isCCTV))
                    else:
                        urls.append(xiyou_parser(video['videoFilePath'],isCCTV))
        else:
	    info = json.loads(get_html('http://vdn.apps.cntv.cn/api/getHttpVideoInfo.do?pid='+id).decode('utf-8'))
	    title = title or info['title']
	    video = info['video']
	    alternatives = [x for x in video.keys() if x.startswith('chapters')]
	    assert alternatives in (['chapters'], ['chapters', 'chapters2']), alternatives
	    chapters = video['chapters2'] if 'chapters2' in video else video['chapters']
	    urls = [x['url'] for x in chapters]

	ext = r1(r'\.([^.]+)$', urls[0])
	assert ext in ('flv', 'mp4')
	print 'Video ext: ', ext
	print 'Video url: ', urls
	print 'Video title: ', title
	download_urls(urls, title, str(ext), total_size=None, merge=merge)

def cntv_download(url, merge=True):
        xiyou=False
	html=get_html(url)
	id = r1(r'<!--repaste.video.code.begin-->(\w+)<!--repaste.video.code.end-->', html)
	if not id:
		id = r1(r'http://xiyou.cntv.cn/v-([\w-]+)\.html', url)
	if not id:
		id = r1(r'"videoCenterId","(\w+)"', html)
	if not id:
		raise NotImplementedError(url)
        if 'xiyou.cntv' in url:
            xiyou=True
	cntv_download_by_id(id, merge=merge, xiyou=xiyou)

download = cntv_download
download_playlist = playlist_not_supported('cntv')

def main():
	script_main('cntv', cntv_download)

if __name__ == '__main__':
	main()

