#!/usr/bin/env python
# encoding: utf-8

from pymongo import MongoClient
from bson.objectid import ObjectId
import re
import json
import urllib
import os


def get_items_img_list():
    db = MongoClient('127.0.0.1', 27017)['math']
    items = list(db.item.find({'status': {'$gt': 39}}))
    # items = list(db.item.find({'_id': ObjectId('567b93095417d16ef86ea8b8')}))
    img_list = []
    for item in items:
        img_list.extend(extract_img(item))
    return img_list


def extract_img(item):

    def _deal_qs(_qs):
        ret = ''
        ret += _qs['desc']
        if isinstance(_qs['ans'], list):
            ret += ' '.join(str(_qs['ans']))
        elif isinstance(_qs['ans'], unicode):
            ret += _qs['ans']
        ret += u' '.join(_qs['opts'])
        ret += _qs['exp']
        if 'qs' in _qs:
            for qss in _qs['qs']:
                ret += _deal_qs(qss)
        return ret
    # _img_list = []
    stem_tex = item['data']['stem']
    qs_tex = ''
    for qs in item['data']['qs']:
        qs_tex += _deal_qs(qs)
    item_tex = stem_tex + qs_tex
    item_tex = item_tex.replace(u'\uff1a', u':')
    item_tex = item_tex.replace(u'\uff0e', u'.')
    item_tex = item_tex.replace(u'，', u',')
    _img_list = re.findall(ur'\[\[img\]\](.*?)\[\[/img\]\]', item_tex)
    for idx, img in enumerate(_img_list):
        if 'src' in img:
            _img_list[idx] = json.loads(img)['src']
    return _img_list


def download_img(img_name):
    img_url = 'http://kuailexue.com/data/img/'
    des_root_path = '/Users/zyj/var/data/img'
    des_file_dir = os.path.join(des_root_path, img_name[:2], img_name[2:4])
    if not os.path.isdir(des_file_dir):
        os.makedirs(des_file_dir)
    des_file_path = os.path.join(des_file_dir, img_name)
    if not os.path.isfile(des_file_path):
        urllib.urlretrieve('{}{}'.format(img_url, img_name), des_file_path)
        print 'yes'
    else:
        print des_file_path


def test():
    img_list = get_items_img_list()
    total = len(img_list)
    i = 1
    for img_name in img_list:
        download_img(img_name)
        print i, total
        i += 1
