#!/usr/bin/env python
# encoding: utf-8

import os
import re
import itertools
from operator import itemgetter
from collections import defaultdict
from functools import partial
from tornado.options import options
import logging
import uuid
import shutil


def get_picture(match, dir_name):
    file_name = match.group(2)

    name, ext = os.path.splitext(file_name)
    name_list = [name, name.lower(), name.upper()]
    ext_list = [ext, ext.lower(), ext.upper()]

    logging.info(u'get_picture:{}'.format(os.path.join(dir_name, file_name)))
    for i, j in itertools.product(name_list, ext_list):
        real_name = os.path.join(dir_name, i + j)
        name = i
        if os.path.exists(real_name):
            break
    else:
        logging.info(u'没有找到对应的文件:{}'.format(os.path.join(dir_name, file_name)))
        return ''

    tmpdir = u"tmp_dir/"+str(uuid.uuid1())+"/"

    img_str = u""
    try:
        os.makedirs(tmpdir)
        new_tmp_name = os.path.join(tmpdir, 'tmp_src.jpg')
        if '.tif' in ext_list:
            convert_conf = '-scale 20%'
        else:
            convert_conf = ''
        os.system(u'convert  -density 100 -quality 100 {}  {}  -trim  {}'.format(
            convert_conf, real_name, new_tmp_name).encode('utf-8'))
        if not os.path.exists(new_tmp_name):
            raise Exception('file not exist: ' + new_tmp_name)
        data = open(tmpdir+"tmp_src.jpg", 'rb').read()
        # saved_name = file_manager.save(options.img_store_path, data, 'jpg')
        img_str += u'[[img]]{}[[/img]]'.format(saved_name)
    except Exception as e:
        logging.info(str(e))
    try:
        shutil.rmtree(tmpdir)
    except Exception as e:
        logging.info(str(e))

    logging.info(u'result img: ' + img_str)
    return img_str


def compute_str(line, dir_name):
    def copy_img(line):
        new_line = u''
        last_img = u''
        num_pattern = re.compile(ur'^\d+[^\d\w]+')
        img_pattern = re.compile(ur'^\[\[img\]\][^\[\]]+\[\[/img\]\]\s*$')
        for sentence in line.splitlines(True):
            sentence = sentence.lstrip()
            new_line += sentence
            if last_img:
                if num_pattern.match(sentence):
                    new_line += last_img
                last_img = ''
            elif img_pattern.match(sentence):
                last_img = sentence
            else:
                pass
        return new_line

    def copy_table(line):
        new_line = u''
        last_table = u''
        num_pattern = re.compile(ur'^\d+[^\d\w]+')
        table_pattern = re.compile(ur'^\\begin{array}[\s\S]+?\\end{array}')
        for sentence in line.splitlines(True):
            new_line += sentence
            if last_table:
                if num_pattern.match(sentence):
                    new_line += last_table
                last_table = ''
            elif table_pattern.match(sentence):
                last_table = sentence
            else:
                # 已经为空
                pass
        return new_line

    def decode_table(match):
        def decode_tds(tr):
            tds = []
            td_pattern = re.compile(ur'\[\]')
            for td in td_pattern.split(tr):
                td = td.strip()
                tds.append({'content': td})
            return tds

        tr_pattern = re.compile(ur'\[BH.*?]')
        trs = []
        column_cnt = 0
        for tr in tr_pattern.split(match.group(1)):
            tr = tr.strip()
            if not tr:
                continue
            trs.append({'td': decode_tds(tr)})
            column_cnt = max(column_cnt, len(trs[-1]['td']))

        for tr in trs:
            while len(tr['td']) < column_cnt:
                tr['td'].append({'content': " "})

        if not column_cnt:
            return ''
        table_contents = u''
        for tr in trs:
            for index, td in enumerate(tr['td']):
                table_contents += (
                    (' & ' if index else '') + re.sub(ur'&', ur'\&', td['content']))
            table_contents += ur'\\ \hline '
        return ur"\begin{array}{%s}\hline %s \end{array}" % (
            u'c'.join(['|' for i in range(column_cnt + 1)]), table_contents)

    line = re.sub(ur'〖', '[', line)
    line = re.sub(ur'〗', ']', line)
    line = re.sub(ur'\ue011', '-', line)
    line = re.sub(ur'\[XC\<(.*?)\>.*?\]', ur'[[img]]\1[[/img]]', line)
    line = re.sub(ur'\[TP\<(.*?)\>.*?\]', ur'[[img]]\1[[/img]]', line)
    line = re.sub(ur'\[PS\<(.*?)\>.*?\]', ur'[[img]]\1[[/img]]', line)
    line = re.sub(
        ur'\[XC([^\[\]]+\.(?:tif|jpg|bmp|TIF|JPG|BMP|eps|EPS|AI|ai))[^\[\]]*?\]',
        ur'[[img]]\1[[/img]]', line)
    line = re.sub(
        ur'\[TP([^\[\]]+\.(?:tif|jpg|bmp|TIF|JPG|BMP|eps|EPS|AI|ai))[^\[\]]*?\]',
        ur'[[img]]\1[[/img]]', line)
    line = re.sub(
        ur'\[PS([^\[\]]+\.(?:tif|jpg|bmp|TIF|JPG|BMP|eps|EPS|AI|ai))[^\[\]]*?\]',
        ur'[[img]]\1[[/img]]', line)
    line = re.sub(ur'\[CD#\d\]', ur'[[nn]]', line)
    line = re.sub(ur'\[ZZ[\(（]Z\](.*?)\[ZZ[\)）]\]', ur'[[un]]\1[[/un]]', line)
    line = re.sub(ur'\[BG.*?\]([\s\S]+?)\[BG.*?\]', decode_table, line)
    line = re.sub(ur'(\[\[img\]\])(.*?)(\[\[/img\]\])',
                  partial(get_picture, dir_name=dir_name), line)

    line = copy_img(line)
    line = copy_table(line)
    line = re.sub(ur'＜', '<', line)
    line = re.sub(ur'＞', '>', line)
    line = re.sub(ur'＝', '=', line)
    line = re.sub(ur'）', ')', line)
    line = re.sub(ur'（', '(', line)
    line = re.sub(ur'÷', r'\\div ', line)
    line = re.sub(ur'×', r'\\times ', line)
    line = re.sub(ur'\[MQ.*?\](.*?)\[MQ\)?\]', ur'[[cd]]\1[[/cd]]', line) # chapter
    line = re.sub(ur'\n\[ML\]\[HS(\d)\](.*?)\[HT\]', ur'[[sd-\1]]\2[[/sd]]', line) # section
    line = re.sub(ur'\[HTH\](.*?)([^］]s*)\[HT\]', ur'[[kp]](\1)[[/kp]]', line) # knowledge point
    return line.encode('gb18030').decode('gbk', 'ignore')


def compute_math(line):
    line = re.sub(ur'\n(?=\n)', '', line)
    line = re.sub(ur'\r', '', line)
    line = re.sub(ur'', '\'', line)
    line = re.sub(ur'', '\n', line)
    line = re.sub(ur'', '\n', line)
    line = re.sub(ur'〖', '[', line)
    line = re.sub(ur'〗', ']', line)
    line = re.sub(ur'）', ')', line)
    line = re.sub(ur'（', '(', line)
    pattern_list = [  # (ur'\ue008','{'),
        (ur'\ue055', r'\\exists '),
        (ur'\u222b', r'\\int '),
        (ur'\u2229', r'\\cap '),
        (ur'\u2264', r'\\leq '),
        (ur'\u22a5', r'\\perp '),
        (ur'\u0391', 'A'),
        (ur'\u039b', r'\\Lambda '),
        (ur'\u03a0', r'\\Pi '),
        (ur'\u03a6', r'\\Phi '),
        (ur'\u03b1', r'\\alpha '),
        (ur'\u03b6', r'\\zeta '),
        (ur'\u03bb', r'\\lambda '),
        (ur'\u03c0', r'\\pi '),
        (ur'\u03c6', r'\\varphi '),
        (ur'\u2211', r'\\sum '),
        (ur'\u222a', r'\\cup '),
        (ur'\u2265', r'\\geq '),
        (ur'\u0088', r'\\in '),
        (ur'\u0392', 'B'),
        (ur'\u03b2', r'\\beta '),
        (ur'\u03b7', r'\\eta '),
        (ur'\u03bc', r'\\mu '),
        (ur'\u03c1', r'\\rho '),
        (ur'\u03c7', r'\\chi '),
        (ur'(?<![\ue00b\ue00c])\ue008(.*?)\ue009', r'\1'),
        (ur'\ue008(.*?)\ue009', r'{\1}'),
        (ur'(\ue00b)+', '^'),
        (ur'\u00b1', r'\\pm '),
        (ur'\u25b3', r'\\triangle '),
        (ur'\u2225', r'\\parallel '),
        (ur'\u0393', r'\\Gamma '),
        (ur'\u0398', r'\\Theta '),
        (ur'\u03a2', r'\\sigma '),
        (ur'\u03a3', r'\\sigma '),
        (ur'\u03a8', r'\\Psi '),
        (ur'\u03b3', r'\\gamma '),
        (ur'\u03b8', r'\\theta '),
        (ur'\u03bd', r'\\nu '),
        (ur'\u03c2', r'\\sigma '),
        (ur'\u03c3', r'\\sigma '),
        (ur'\u03c8', r'\\psi '),
        (ur'(\ue00c)+', '_'),
        (ur'\u00b0', r'^\\circ '),
        (ur'\ue07e', r'\\varnothing '),
        (ur'\u0394', r'\\Delta '),
        (ur'\u039e', r'\\Xi '),
        (ur'\u03a9', r'\\Omega '),
        (ur'\u03b4', r'\\delta '),
        (ur'\u03b9', r'\\iota '),
        (ur'\u03be', r'\\xi '),

        (ur'\u03c4', r'\\tau '),
        (ur'\u03c9', r'\\omega '),
        (ur'\u221e', r'\\infty '),
        (ur'\u2220', r'\\angle '),
        (ur'\u03a5', r'\\Upsilon '),
        (ur'\u03ba', r'\\epsilon '),
        (ur'\u03ba', r'\\kappa '),
        (ur'\u03c5', r'\\upsilon ')
    ]

    for src_str, des_str in pattern_list:
        line = re.sub(src_str, des_str, line)

    line = re.sub(ur'\[WTHZ\]', r'', line)
    line = re.sub(ur'\[WTHX\]', r'', line)
    line = re.sub(ur'\[WTBX\]', r'', line) # font setting 
    line = re.sub(ur'\[MQ.*?\](.*?)\[MQ\)?\]', ur'[[cd]]\1[[/cd]]', line)
    line = re.sub(ur'\n\[ML\]\[HS(\d)\](.*?)\[HT\]', ur'[[sd-\1]]\2[[/sd]]', line)
    line = re.sub(ur'\[HTH\](.*?)([^］]s*)\[HT\]', ur'[[kp]](\1)[[/kp]]', line)
    line = re.sub(ur'(?<!=)(\d+)\[BFQ\]\.\[BF\](?!\[JB\])', ur'[[qnum]]\1[[/qnum]].', line)
    line = re.sub(ur'\ue00a([A-Ga-g])\ue00a\[BFQ\]\.\[BF\]', ur'[[op]]\1[[/op]].', line)
    line = re.sub(ur'\ue00a(.*?)\ue00a', r'{\\rm{\1}}}', line)
    line = re.sub(ur'\ue008(.*?)\ue009\[TX\u2192\]', r'{\\overrightarrow {\1}}', line)
    line = re.sub(ur'\[AK(.*?)\-\]', r'\\overline \1', line)
    line = re.sub(ur'\[KF\(S\](\d+)\[\](.*?)\[KF\)\]', r'\\sqrt[\1]{\2}', line)
    line = re.sub(ur'\[KF\(\](.*?)\[KF\)\]', r'{\\sqrt{\1}}', line)
    line = re.sub(ur'\[SX\(\](.*?)\[\](.*?)\[SX\)\]', r'{\\dfrac{\1}{\2}}', line)
    line = re.sub(ur'\u2211\[DD\(\](.*?)\[\](.*?)\[DD\)\]', r'\\sum\\limits_{\2}^{\1}', line)
    line = re.sub(ur'\[JX\-\*4\]\ue020\[JX\*4\]', r'\\subseteq', line)
    line = re.sub(ur'\[FK\(W\]\[HT7,5\]\u2510\[FK\)\]\[KG\-\*4/9\]', r'\\neg ', line)
    line = re.sub(ur'\[JB\({\](.*?),(.*?)\)\.\[JB\)\]',
                  r'\\begin{cases} \1 \\\\ \2 \\end{cases}', line)
    line = re.sub(ur'\[JB\({\](.*?),(.*?),(.*?)\)\.\[JB\)\]',
                  r'\\begin{cases} \1 \\\\ \2  \\\\  \3 \\end{cases}', line)
    line = re.sub(ur'\[JB\uff0b\]\[HL\(2\](.*?)\[\](.*?)\ue003(.*?)\[\](.*?)\[HL\)\]\[JB\)\uff3d\]',
                  r'\\begin{matrix} \1 & \2 \\\\ \3 & \4 \\end{matrix}', line)

    line = re.sub(
        ur'\ue008\ue008(.*?)\ue009\[TXX}\]\ue009\[DD\(X\*2\]\ue008(.*?)\ue009\[DD\)\]',
        r'\\underbrace {\1} _{\2}', line)

    return line


def split_line(lines):
    def normalize_line(line):
        line = re.sub(ur'\[PN.*?\[PN\)?\]', u'', line)
        line = re.sub(ur'\[BW.*?\[BW\)?\]', u'', line)

        line = re.sub(ur'\[JY\]\{?\(〓+\)\}?', ur'[[nn]]', line)
        line = re.sub(ur'(?<!\[)\[[^\"\'\[\]]{2,}\](?!\])', ' ', line)
        line = re.sub(ur'(?<!\[)\[[a-zA-Z]\](?!\])', ' ', line)
        line = re.sub(ur'(?<!\[)\[\](?!\])', ' ', line)
        line = re.sub(ur'[〓]+(?=\()', '\n', line)
        line = re.sub(ur'[〓]+', ' ', line)
        line = u'\n'.join([_.strip() for _ in line.splitlines()])
        line = re.sub(ur'\n{2,}', ur'\n', line)
        line = re.sub(ur'\[\[un\]\](\{?)\s+(\}?)\[\[/un\]\]', ur'\1[[nn]]\2', line)
        return line
    split_patten = re.compile(ur'\[FL\)')
    lines = split_patten.split(lines)
    return [normalize_line(line) for line in lines]


def search_and_extract(dir_name):
    def _get_files(path):
        assert os.path.isdir(path)
        return [os.path.join(path, file_name) for file_name in os.listdir(path)]

    assert os.path.isdir(dir_name)
    files = [os.path.join(dir_name, file_name) for file_name in os.listdir(dir_name)]
    return_name = defaultdict(lambda: {'question': '', 'answer': '', 'index': 0})
    return_data = defaultdict(lambda: {'question': '', 'answer': '', 'index': 0})

    while files:
        file_name = files.pop()
        if os.path.isdir(file_name):
            files += _get_files(file_name)
        elif file_name.endswith('.fbd'):
            dir_name, basename = os.path.split(file_name)
            name, _ = os.path.splitext(basename)
            if name not in [u'教师详答', u'正文']:
                continue
            type_id = 'question' if name == u'正文' else 'answer'
            line = open(file_name).read()
            line = line.decode('gb18030', 'ignore')
            line = compute_math(line)
            line = compute_str(line, dir_name)
            lines = split_line(line)
            for index, line in enumerate(lines):
                file_name = file_manager.save(
                    options.doc_store_path, line.encode('utf-8'), 'txt')
                return_name[index][type_id] = file_name
                return_name[index]['index'] = index
                return_data[index][type_id] = line
                return_data[index]['index'] = index
    return sorted(return_name.values(), key=itemgetter('index')),\
        sorted(return_data.values(), key=itemgetter('index'))

dir_name = ''
file_name = u'正文.fbd'
f = open(file_name)
line = f.read()
line = line.decode('gb18030', 'ignore')
line = compute_math(line)
line = compute_str(line, dir_name)
lines = split_line(line)
for line in lines:
    print line



