#!/usr/bin/env python
# -*- coding: utf-8 -*-
import _env
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter
from extract import extract_map

def deal(code):
    lang_name = code.split()[1][:-1]
    code = '\n'.join(code.split('\n')[1:-1])
    lexer = get_lexer_by_name(lang_name)
    formatter = HtmlFormatter(linenos=True)
    return highlight(code, lexer, formatter)

def highlight_txt(txt):   
    return extract_map('<code', '</code>', txt, deal)

if __name__ == '__main__':
    code ='''
首先是extract：
<code py>
#coding:utf-8
import re

def extract(begin, end, html):
    if not html:
        return ''
    start = html.find(begin)
    if start >= 0:
        start += len(begin)
</code>

然后是爬虫框架，下面是原版
<code py>
#coding:utf-8
import _env
from gevent.queue import Empty, Queue
import gevent

class Route(object):
    def __init__(self):
        self.map = []
</code>

'''
    print highlight_txt(code)
