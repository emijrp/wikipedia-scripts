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
import time
import urllib
import urllib.request

import pwb
import pywikibot
from pywikibot import pagegenerators

def replaceAuthor(newtext=''):
    newtext = re.sub(r'(?im)(\|\s*author\s*=\s*)\[\[User\:Emijrp\|Emijrp\]\]', r'\1{{User:Emijrp/credit}}', newtext)
    newtext = re.sub(r'(?im)(\|\s*author\s*=\s*)User\:Emijrp', r'\1{{User:Emijrp/credit}}', newtext)
    newtext = re.sub(r'(?im)(\|\s*author\s*=\s*)Usuario\:Emijrp', r'\1{{User:Emijrp/credit}}', newtext)
    newtext = re.sub(r'(?im)(\|\s*author\s*=\s*)Emijrp', r'\1{{User:Emijrp/credit}}', newtext)
    return newtext

def replaceSource(newtext=''):
    if re.search(r'(?im)\|\s*author\s*=\s*{{User:Emijrp/credit}}', newtext):
        newtext = re.sub(r'(?im)(\|\s*source\s*=\s*){{User:Emijrp/credit}}', r'\1{{own work}}', newtext)
    return newtext

def creditByWhatlinkshere():
    commons = pywikibot.Site('commons', 'commons')
    userpage = pywikibot.Page(commons, 'User:Emijrp')
    gen = userpage.backlinks(namespaces=[6])
    for page in gen:
        print('==', page.title(), '==')
        newtext = page.text
        newtext = replaceAuthor(newtext=newtext)
        newtext = replaceSource(newtext=newtext)
        if newtext != page.text:
            pywikibot.showDiff(page.text, newtext)
            page.text = newtext
            page.save('BOT - Updating credit template')

def creditByCategory():
    commons = pywikibot.Site('commons', 'commons')
    category = pywikibot.Category(commons, '15-O Demonstrations, Cádiz')
    category = pywikibot.Category(commons, 'Paseo reflexivo Cádiz 21 de mayo de 2011')
    gen = pagegenerators.CategorizedPageGenerator(category)
    for page in gen:
        print('==', page.title(), '==')
        newtext = page.text
        newtext = replaceAuthor(newtext=newtext)
        newtext = replaceSource(newtext=newtext)
        if newtext != page.text:
            pywikibot.showDiff(page.text, newtext)
            page.text = newtext
            page.save('BOT - Updating credit template')

def creditByFlickrUrl():
    commons = pywikibot.Site('commons', 'commons')
    flickrurls = [
        'http://flickr.com/people/96396586@N07',
        'http://www.flickr.com/people/96396586@N07',
        'https://flickr.com/people/96396586@N07',
        'https://www.flickr.com/people/96396586@N07',
    ]
    for flickrurl in flickrurls:
        images = ['hola']
        while images:
            linksearch = 'https://commons.wikimedia.org/w/index.php?target=%s&title=Special:LinkSearch' % (flickrurl)
            req = urllib.request.Request(linksearch, headers={ 'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:55.0) Gecko/20100101 Firefox/55.0' })
            raw = urllib.request.urlopen(req).read().strip().decode('utf-8')
            images = re.findall(r'title="(File:[^<>]+?)">File:', raw)
            print(images)
            for image in images:
                page = pywikibot.Page(commons, image)
                text = page.text
                newtext = page.text
                newtext = re.sub(r'(\|\s*Author\s*=\s*)\[%s [^\]]*?\]\s*(de|from)?\s*(España|Spain)?' % (flickrurl), r'\1{{User:Emijrp/credit}}', newtext)
                if text != newtext:
                    pywikibot.showDiff(text, newtext)
                    page.text = newtext
                    page.save('BOT - Updating credit template')

def main():
    creditByFlickrUrl()
    #creditByCategory()
    #creditByWhatlinkshere()

if __name__ == '__main__':
    main()
