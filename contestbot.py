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

def removeNoProse(text='', keeprefs=False, keepinlinetemplates=False, keeplists=True):
    for y in range(10, 0, -1):
        for x in ['Bibliography', 'Citations', 'Notes', 'References', 'See also', 'External links']:
            text = text.split('%s%s' % (y*'=', x))[0]
            text = text.split('%s %s' % (y*'=', x))[0]
            text = text.split('%s  %s' % (y*'=', x))[0]
    text = re.sub(r'(?im)\'\'+', r'', text)
    if not keepinlinetemplates:
        text = re.sub(r'(?im).\{\{[^\{\}]*?\}\}', r' ', text)
    text2 = []
    for line in text.splitlines():
        line = line.strip()
        if len(line) < 15:
            continue
        if not line or \
            line.startswith('{') or \
            line.startswith('|') or line.startswith(' |') or line.startswith('  |') or \
            line.startswith('}') or \
            line.startswith('!') or line.startswith(' !') or line.startswith('  !') or \
            line.startswith('*{{') or line.startswith('* {{'):
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
    if not keeplists:
        text = re.sub(r'(?im)^\*.{3,}', r'', text)
    text = re.sub(r'  +', r' ', text)
    text = re.sub(r'(?im)[\r\n\s]+\|[\r\n\s]+', ' | ', text) #remove newlines inside refs
    text = re.sub(r'(?im)([^\.])[\n\r]+', r'\1', text) #remove ghost lines, lines that doesnt end in a dot, etc
    text = text.strip()
    return text

def proseCount(text=''):
    for i in range(1, 10):
        text = removeNoProse(text=text, keeprefs=False, keepinlinetemplates=False, keeplists=False)
    return len(text)

def unsourcedParagraphs(text=''):
    unsourced = 0
    sections = set(re.findall(r'(?im)^==\s*([^=]+?)\s*==', text))
    for x in ['Bibliography', 'Citations', 'Notes', 'References', 'See also', 'External links']:
        if x in sections:
            sections.remove(x)
    text = removeNoProse(text=text, keeprefs=True, keepinlinetemplates=True)
    #print(text.encode('utf-8'))
    c = 1
    for line in text.splitlines():
        if c == 1: #ignore unsourced leads if there are sections below
            c += 1
            if sections or len(re.findall(r'(?im)(<\s*ref|\{\{sfn)', text)) >= 2:
                #print(sections)
                continue
        line = line.strip()
        if line and \
            not re.search(r'(?im)<\s*ref[ \>]', line) and \
            not re.search(r'(?im)\{\{sfn', line) and \
            not re.search(r'(?im)http', line) and \
            not re.search(r'(?im)^[\*\#]', line):
            unsourced += 1
            print("UNSOURCED: %s" % (line.encode('utf-8')))
        c += 1
    #print('unsourced', unsourced)
    return unsourced

def formatErrors(text=''):
    errors = []
    if re.search(r'(?im)http', text) and not re.search(r'(?im)[\[\=]\s*http', text): #plain urls
        errors.append('plain url')
    if not re.search(r'(?im)(\{\{\s*sfn|ref\s*=\s*harv|\{\{\s*harv)', text):
        if len(re.findall(r'(?im)(journal|publisher|newspaper|website|work)\s*=\s*[^\|\=\s]', text)) < len(re.findall(r'(?im)\{\{\s*cite', text)): #refs without publisher
            errors.append('missing publisher')
        if re.findall(r'(?im)date\s*=\s*\d\d\d\d\-', text) and re.findall(r'(?im)date\s*=\s*(\d+ )?(Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Oct|Nov|Dec)', text): #mix date formats
            errors.append('date format')
    #print('errors', errors)
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
        print('== %s ==' % (contestpagetitle.encode('utf-8')))
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
                m = re.findall(r'(?im)^([\*\#]\s*\[\[[^\[\]]+?\]\].*)', line)
                if m:
                    m = m[0]
                    if not 'Wikipedia:' in m: # and not 'prose count' in m:
                        pagetitle = re.sub(r'(?im)[\[\]\*\#]', r'', m.split('|')[0].split(']')[0].strip()).strip()
                        print(pagetitle.encode('utf-8'))
                        page = pywikibot.Page(site, pagetitle)
                        if page.isRedirectPage():
                            page = page.getRedirectTarget()
                            pagetitle = page.title()
                        newline = '* [[%s]] - ' % (pagetitle)
                        
                        #valid namespace
                        if page.namespace() != 0:
                            newline += 'Declined, entry isn\'t in main namespace'
                            newtext.append(newline)
                            continue
                        
                        #valid date range
                        firstedit = page.getVersionHistory(total=1, reverse=True)[0]
                        summaries = '\n'.join([x[3] for x in page.getVersionHistory()])
                        #print(summaries.encode('utf-8'))
                        if not str(firstedit.timestamp).startswith('2017-11-'):
                            if re.search(r"(?im)moved page \[\[(Draft|User):", summaries):
                                newline += 'Created in User or Draft space and submitted within November. {{tick}} '
                            else:
                                newline += 'Declined, entry wasn\'t created in November. {{cross}}'
                                newtext.append(newline)
                                continue
                        
                        #analysis
                        count = proseCount(text=page.text)
                        if count >= 1000:
                            newline += 'Readable prose count: %s bytes. {{tick}} ' % (count)
                        else:
                            newline += 'Readable prose count: %s bytes. {{cross}} ' % (count)
                        unsourced = unsourcedParagraphs(text=page.text)
                        formaterrors = formatErrors(text=page.text)
                        if unsourced or formaterrors:
                            newline += 'Unsourced paragraphs (%s), formatting errors%s. {{cross}}' % (unsourced, formaterrors and ' (%s)' % (', '.join(formaterrors)) or ' (none)')
                        else:
                            newline += 'No unsourced paragraphs, no formatting errors. {{tick}}'
                        newtext.append(newline)
                        #print(newline.encode('utf-8'))
                        continue
            newtext.append(line)
        newtext = '\n'.join(newtext)
        if text != newtext:
            pywikibot.showDiff(text, newtext)
            contestpage.text = newtext
            contestpage.save('BOT - Checking articles')

if __name__ == '__main__':
    main()
