#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2017 emijrp <emijrp@gmail.com>
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import re

import pwb
import pywikibot
from pywikibot import pagegenerators

def removeNoProse(text='', keeprefs=False):
    for y in range(10, 0, -1):
        for x in ['Bibliography', 'Citations', 'Notes', 'References', 'See also']:
            text = text.split('%s%s' % (y*'=', x))[0]
            text = text.split('%s %s' % (y*'=', x))[0]
            text = text.split('%s  %s' % (y*'=', x))[0]
    text = re.sub(r'(?im)\'\'+', r'', text)
    #text = re.sub(r'(?im)\{\{[^\{\}]*?\}\}', r' ', text)
    text2 = []
    for line in text.splitlines():
        line = line.strip()
        if len(line) < 15:
            continue
        if not line or \
            line.startswith('{') or \
            line.startswith('|') or \
            line.startswith('}'):
            continue
        text2.append(line)
    text = '\n'.join(text2)
    text = re.sub(r'(?im)^==+[^=]*?==+', r' ', text)
    text = re.sub(r'(?im)\[\[\s*(File|Image)\s*:.*?\]\]', r' ', text)
    if not keeprefs:
        text = re.sub(r'(?im)<ref[^<>]*?>[^<>]*?</ref>', r' ', text)
        text = re.sub(r'(?im)<ref[^<>]*?>', r' ', text)
        text = re.sub(r'(?im)\{\{sfn[^\{\}]*?\}\}', r' ', text)
    text = re.sub(r'(?im)\[\[\s*Category\s*:[^\[\]]*?\]\]', r' ', text)
    text = re.sub(r'  +', r' ', text)
    text = re.sub(r'\n\n+', r'\n', text)
    text = re.sub(r'(?im)\[\[([^\[\]\|]*?)\]\]', r'\1', text)
    text = re.sub(r'(?im)\[\[[^\[\]\|]*?\|([^\[\]\|]*?)\]\]', r'\1', text)
    text = text.strip()
    return text

def proseCount(text=''):
    for i in range(1, 10):
        text = removeNoProse(text=text)
    return len(text)

def unsourcedParagraphs(text=''):
    unsourced = 0
    text = removeNoProse(text=text, keeprefs=True)
    #print(text)
    c = 1
    for line in text.splitlines():
        if c == 1:
            c += 1
            continue
        line = line.strip()
        if line and \
            not re.search(r'(?im)<\s*ref[ \>]', line) and \
            not re.search(r'(?im)\{\{sfn', line):
            unsourced += 1
        c += 1
    print('unsourced', unsourced)
    return unsourced

def formatErrors(text=''):
    errors = []
    if re.search(r'(?im)http', text) and not re.search(r'(?im)[\[\=]\s*http', text): #plain urls
        errors.append('plain url')
    if len(re.findall(r'(?im)publisher\s*=', text)) != len(re.findall(r'(?im)\{\{\s*cite', text)): #refs without publisher
        errors.append('missing publisher')
    if re.findall(r'(?im)date\s*=\s*\d\d\d\d\-', text) and re.findall(r'(?im)date\s*=\s*(\d+ )?(Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Oct|Nov|Dec)', text):
        errors.append('date format')
    print('errors', errors)
    return errors

def main():
    site = pywikibot.Site('en', 'wikipedia')
    contestpagetitles = [
        'Wikipedia:WikiProject Women in Red/The World Contest/Entries/North America', 
        'Wikipedia:WikiProject Women in Red/The World Contest/Entries/Latin America and the Caribbean', 
        'Wikipedia:WikiProject Women in Red/The World Contest/Entries/Europe', 
        'Wikipedia:WikiProject Women in Red/The World Contest/Entries/Africa', 
        'Wikipedia:WikiProject Women in Red/The World Contest/Entries/Asia', 
        'Wikipedia:WikiProject Women in Red/The World Contest/Entries/Oceania', 
    ]
    for contestpagetitle in contestpagetitles:
        print('== %s ==' % (contestpagetitle))
        contestpage = pywikibot.Page(site, contestpagetitle)
        text = contestpage.text
        lines = text.splitlines()
        newtext = []
        usersection = False
        for line in lines:
            if re.search(r'(?im)^==.*User', line):
                usersection = True
                newtext.append(line)
                continue
            if usersection and re.search(r'(?im)^==', line):
                usersection = False
                newtext.append(line)
                continue
            
            if usersection:
                m = re.findall(r'(?im)^(\*\s*\[\[[^\[\]]+?\]\]).*', line)
                if m:
                    m = m[0]
                    if not 'Wikipedia:' in m and not 'prose count' in m:
                        pagetitle = re.sub(r'(?im)[\[\]\*]', r'', m.split('|')[0].strip()).strip()
                        #pagetitle = 'María Stagnero de Munar'
                        print(pagetitle)
                        page = pywikibot.Page(site, pagetitle)
                        newline = '* [[%s]] - ' % (pagetitle)
                        count = proseCount(text=page.text)
                        if count >= 1000:
                            newline += 'Readable prose count: %s bytes. {{tick}} ' % (count)
                        else:
                            newline += 'Readable prose count: %s bytes. {{cross}} ' % (count)
                        unsourced = unsourcedParagraphs(text=page.text)
                        formaterrors = formatErrors(text=page.text)
                        if unsourced or formaterrors:
                            newline += 'Unsourced paragraphs (%s); formatting errors%s. {{cross}}' % (unsourced, formaterrors and ' (%s)' % (', '.join(formaterrors)) or 'none')
                        else:
                            newline += 'No unsourced paragraphs; no formatting errors. {{tick}}'
                        newtext.append(newline)
                        print(newline)
                        continue
            newtext.append(line)
        newtext = '\n'.join(newtext)
        if text != newtext:
            pywikibot.showDiff(text, newtext)
            contestpage.text = newtext
            contestpage.save('BOT - Checking articles')

if __name__ == '__main__':
    main()
