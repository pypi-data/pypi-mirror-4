#!/usr/bin/env python
#coding:utf-8
def cap_split(phrase, li=[]):
    #把一个字符串根据单词split
    #print cap_split('FuckMyAssHole')
    #>>['Fuck', 'My', 'Ass', 'Hole']
    def find_next_upper(s, start):
        for n, i in enumerate(s[start:]):
            if i.upper() == i:
                return n + start
    for n, i in enumerate(phrase):
        if i.upper() == i:
            next_loc = find_next_upper(phrase, n+1)
            if next_loc:
                li.append(phrase[:next_loc])
                return cap_split(phrase[next_loc:], li)
            else:
                li.append(phrase)
                return li

if __name__ == "__main__":
    print cap_split('FuckMyAssHole')
    pass
