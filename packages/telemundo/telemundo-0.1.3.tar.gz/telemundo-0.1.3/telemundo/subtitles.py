#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re, codecs
from os import path
from xml.sax import saxutils
from datetime import datetime
from HTMLParser import HTMLParser

class CaptionGenerator():
    captions = None
    language = None

    def __init__(self, language='en-US'):
        self.captions = []
        self.language = language

    def __len__(self):
        return len(self.captions)

    def insert(self, caption):
        self.captions.append(caption)

    def export(self, filename):
        fp = codecs.open(filename, 'w', 'utf-8')
        fp.write(u'<?xml version="1.0" encoding="utf-8"?>\n')
        fp.write(u'<tt xml:lang="%s" xmlns="http://www.w3.org/2006/10/ttaf1">\n' % self.language)
        fp.write(u'  <head>\n')
        fp.write(u'    <metadata xmlns:ttm="http://www.w3.org/2006/10/ttaf1#metadata">\n')
        fp.write(u'      <ttm:copyright>Telemundo Digital Media, all rights reserved</ttm:copyright>\n')
        fp.write(u'      <ttm:description>Generated on %s UTC</ttm:description>\n' % datetime.utcnow())
        fp.write(u'    </metadata>\n')
        fp.write(u'  </head>\n')
        fp.write(u'  <body>\n')
        fp.write(u'    <div>\n')
        if len(self.captions) > 0:
            for caption in self.captions:
                line = u'      <p xml:id="caption-%d" begin="%s" end="%s">%s</p>\n' % (caption['pos'], caption['begin'], caption['end'], caption['text'])
                fp.write(line)
        fp.write(u'    </div>\n')
        fp.write(u'  </body>\n')
        fp.write(u'</tt>\n')
        fp.close()

class CaptionParser(HTMLParser):
    stack = None

    def __init__(self):
        self.stack = []
        self.reset()

    def handle_data(self, data):
        self.stack.append(saxutils.escape(data))

    def clean(self):
        return unicode(u''.join(self.stack))

class SubtitleParser():
    def __parse_srt_file(self, filename):
        lines = codecs.open(filename, 'r', 'utf-8').read().encode('utf-8')

        return re.findall(r'(?P<data>.*?)\r?\n\r?\n', lines, re.MULTILINE + re.DOTALL)

    def __create_srt_caption(self, caption):
        lines = caption.splitlines()
        position = int(lines.pop(0))
        timecodes = map(lambda x: x.replace(',', '.'), lines.pop(0).split(' --> '))
        text = u'%s' % u'\n'.join([line.decode('utf-8') for line in lines])

        return {
            'pos': position,
            'begin': timecodes[0],
            'end': timecodes[1],
            'text': text
        }

    def parse(self, filename, language):
        if not path.exists(filename):
            raise ValueError('The subtitle file "%s" does not exist.' % filename)

        generator = CaptionGenerator(language)
        matches = self.__parse_srt_file(filename)
        for match in matches:
            caption = self.__create_srt_caption(match)
            if caption:
                parser = CaptionParser()
                parser.feed(caption['text'])
                caption['text'] = parser.clean();
                generator.insert(caption)
        
        return generator
