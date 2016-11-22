#!/usr/bin/env python
# encoding: utf-8

fbd_qcode_map = [
	{
		'name': '_cd',
		'sub':  ur'[[cd]]\1[[/cd]]'	,
		'ori': [ur'\[MQ.*?\](.*?)\[MQ\)?\]'],
	},
	{
		'name': '_sd',
		'sub': ur'[[sd-\1]]\2[[/sd]]',
		'ori': [ur'\n\[ML\]\[HS(\d)\](.*?)\[HT\]'],
	},
	{
		'name': '_kp',
		'sub': ur'[[kp]](\1)[[/kp]]',
		'ori': [ur'\[HTH\](.*?)([^］]s*)\[HT\]'],
	},
	{
		'name': '_q_num',
		'sub': ur'[[qnum]]\1[[/qnum]].',
		'ori': [ur'(?<!=)(\d+)\[BFQ\]\.\[BF\](?!\[JB\])'],
	},
	{
		'name': '_op',
		'sub': ur'[[op]]\1[[/op]].',
		'ori': [ur'\ue00a([A-Ga-g])\ue00a\[BFQ\]\.\[BF\]'],
	},
	{
		'name': '_img',
		'sub': ur'[[img]]\1[[/img]]',
		'ori': [
                ur'\[XC([^\[\]]+\.(?:tif|jpg|bmp|TIF|JPG|BMP|eps|EPS|AI|ai))[^\[\]]*?\]',
                ur'\[TP([^\[\]]+\.(?:tif|jpg|bmp|TIF|JPG|BMP|eps|EPS|AI|ai))[^\[\]]*?\]',
                ur'\[PS([^\[\]]+\.(?:tif|jpg|bmp|TIF|JPG|BMP|eps|EPS|AI|ai))[^\[\]]*?\]',
            ],
	}
]
