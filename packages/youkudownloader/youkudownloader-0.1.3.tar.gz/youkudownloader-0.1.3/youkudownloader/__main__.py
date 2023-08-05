#!/usr/bin/env python

import acfun
import bilibili
import chinanews
import cntv
import ifeng
import iqiyi
import ku6
import letv
import mtime
import pptv
import qq
import sina
import sohu
import tudou
import w56
import yesky
import yinyuetai
import youku
import zol

from common import *
import re

def url_to_module(url):
	site = r1(r'http://([^/]+)/', url)
	assert site, 'invalid url: ' + url
	if site.endswith('.com.cn'):
		site = site[:-3]
	domain = r1(r'(\.[^.]+\.[^.]+)$', site)
	assert domain, 'not supported url: ' + url
	k = r1(r'([^.]+)', domain)
	downloads = {
			'youku':youku,
			'bilibili':bilibili,
			'zol':zol,
			'kankanews':bilibili,
			'smgbb':bilibili,
			'acfun':acfun,
			'sina':sina,
			'ku6':ku6,
			'mtime':mtime,
			'pptv':pptv,
			'iqiyi':iqiyi,
			'tudou':tudou,
			'sohu':sohu,
			'chinanews':chinanews,
			'56':w56,
			'yesky':yesky,
			'letv':letv,
			'qq':qq,
			'cntv':cntv,
			'yinyuetai':yinyuetai,
			'ifeng':ifeng,
	}
	if k in downloads:
		return downloads[k]
	else:
		raise NotImplementedError(url)

def any_download(url, merge=True):
	m = url_to_module(url)
	m.download(url, merge=merge)

def any_download_playlist(url, create_dir=False, merge=True):
	m = url_to_module(url)
	m.download_playlist(url, create_dir=create_dir, merge=merge)

def main():
	script_main('main', any_download, any_download_playlist)

if __name__ == '__main__':
	main()


