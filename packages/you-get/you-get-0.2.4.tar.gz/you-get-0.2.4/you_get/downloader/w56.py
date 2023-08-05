#!/usr/bin/env python

__all__ = ['w56_download', 'w56_download_by_id']

from ..common import *

import json

def w56_download_by_id(id, title = None, output_dir = '.', merge = True, info_only = False):
    info = json.loads(get_html('http://vxml.56.com/json/%s/?src=site' % id))['info']
    title = title or info['Subject']
    assert title
    hd = info['hd']
    assert hd in (0, 1, 2)
    type = ['normal', 'clear', 'super'][hd]
    files = [x for x in info['rfiles'] if x['type'] == type]
    assert len(files) == 1
    size = int(files[0]['filesize'])
    url = files[0]['url']
    ext = r1(r'\.([^.]+)$', url)
    assert ext in ('flv', 'mp4')
    
    print_info(site_info, title, ext, size)
    if not info_only:
        download_urls([url], title, ext, size, output_dir = output_dir, merge = merge)

def w56_download(url, output_dir = '.', merge = True, info_only = False):
    id = r1(r'http://www.56.com/u\d+/v_(\w+).html', url)
    w56_download_by_id(id, output_dir = output_dir, merge = merge, info_only = info_only)

site_info = "56.com"
download = w56_download
download_playlist = playlist_not_supported('56')
