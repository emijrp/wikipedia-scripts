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

def main():
    commons = pywikibot.Site('commons', 'commons')
    images = ['hola']
    while images:
        flickrurl = 'https://www.flickr.com/people/96396586@N07'
        linksearch = 'https://commons.wikimedia.org/w/index.php?target=%s&title=Special:LinkSearch' % (flickrurl)
        req = urllib.request.Request(linksearch, headers={ 'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:55.0) Gecko/20100101 Firefox/55.0' })
        raw = urllib.request.urlopen(req).read().strip().decode('utf-8')
        images = re.findall(r'title="(File:[^<>]+?)">File:', raw)
        print(images)
        for image in images:
            page = pywikibot.Page(commons, image)
            text = page.text
            newtext = page.text
            newtext = re.sub(r'(\|\s*Author\s*=\s*)\[https://www.flickr.com/people/96396586@N07 [^\]]*?\] from España', r'\1{{User:Emijrp/credit}}', newtext)
            if text != newtext:
                pywikibot.showDiff(text, newtext)
                page.text = newtext
                page.save('BOT - Updating credit template')

if __name__ == '__main__':
    main()
