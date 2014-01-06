#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  makeCUE.py
#  
#  Copyright 2014 Coren <Coren.mail@gmail.com>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  

from datetime import datetime
import re, sys
import argparse

def loadChapters(chapter_file):
    '''
    Read an eac3to chapters file and extracts indices, timestamps and 
    track titles.
    
    A chapter file should look something like this:
    
    '''

    example = '''
    Invalid chapter file. Chapters should have the following format:

    CHAPTER01=00:00:00.000
    CHAPTER01NAME=
    CHAPTER02=00:18:42.121
    CHAPTER02NAME=
    CHAPTER03=00:28:54.733
    CHAPTER03NAME=
    '''
    
    with open(chapter_file, 'r') as fin:
        lines = [line.strip() for line in fin.readlines() if line.strip()]
    
    re_stamp = re.compile('CHAPTER(\d\d)=(\d\d:\d\d:\d\d.\d\d\d)')
    re_name = re.compile('CHAPTER(\d\d)NAME=(.*)')
    
    chapters = {}
    for line in lines:
        assert line.startswith('CHAPTER'), 'Invalid chapter file. Every line should start with CHAPTER??'
        
        if re.match(re_stamp, line):
            found = re.match(re_stamp, line).groups()
            assert len(found) == 2, example
            num, stamp = int(found[0]), datetime.strptime(found[1], '%H:%M:%S.%f')
            assert num not in chapters, 'Invalid chapter file. Each chapter should only occur once.'
            chapters[num] = [stamp]
        
        elif re.match(re_name, line):
            found = re.match(re_name, line).groups()
            assert len(found) == 2, example
            num, name = int(found[0]), found[1]
            assert num in chapters, example
            if name.strip():
                chapters[num].append(name)
            else:
                chapters[num].append('')
        
        else:
            sys.exit(msg=example)
        
    return chapters

def writeCUE(chapters, audio_file, cue_file, extras):
    '''
    
    Input:
    a dictionary of {chapter_number: [datetime_stamp, track_title}
    the audio file to be linked to the CUE file
    the name of the file to write the output to
    a dictionary of extra info (possible keys: 'artist', 'title',
    'year', 'genre')
    
    Example output:

    REM GENRE "Progressive rock"
    REM DATE "1972"
    PERFORMER "Yes"
    TITLE "Close to the Edge"
    FILE "mc.flac" WAVE
      TRACK 01 AUDIO
        TITLE ""
        INDEX 01 00:00:00
      TRACK 02 AUDIO
        TITLE ""
        INDEX 01 18:42:12
      TRACK 03 AUDIO
        TITLE ""
        INDEX 01 28:54:73
        
    '''
    with open(cue_file, 'w') as fout:
        
        if extras['genre']:
            fout.write('REM GENRE "{0}"\n'.format(extras['genre']))
        if extras['year']:
            fout.write('REM DATE "{0}"\n'.format(extras['year']))
        if extras['artist']:
            fout.write('PERFORMER "{0}"\n'.format(extras['artist']))
        if extras['album']:
            fout.write('TITLE "{0}"\n'.format(extras['album']))
        fout.write('FILE "{0}" WAVE\n'.format(audio_file))

        for num in range(1, len(chapters)+1):
            
            stamp = chapters[num][0]
            hundreths = int(stamp.microsecond/float(10000))
            
            fout.write('  TRACK {0:02d} AUDIO\n'.format(num))
            fout.write('    TITLE "{0}"\n'.format(chapters[num][1]))
            fout.write('    INDEX 01 {0}:{1:02d}\n'.format(datetime.strftime(stamp, '%M:%S'), hundreths))
            
    return cue_file         

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Convert a eac3to chapter file to a foobar2000-ready CUE file.')
    parser.add_argument('chapter_file', metavar='chapter_file', type=str,
                       help='The chapter file from eac3to')
    parser.add_argument('audio_file', metavar='audio_file', type=str,
                       help='The audio file the CUE file should link to')
    parser.add_argument('cue_file', metavar='CUE_file', type=str,
                       help='The name of the CUE file you want to create')
    parser.add_argument('--album', dest='album',
                       help='Specify the album title')
    parser.add_argument('--artist', dest='artist',
                       help='Specify the artist performing the album')
    parser.add_argument('--genre', dest='genre',
                       help='Specify the genre of the album')                  
    parser.add_argument('--year', dest='year',
                       help='Specify the year the album was released')
                       
    args = parser.parse_args()
    
    extras = {
                'album': args.album,
                'artist': args.artist,
                'genre': args.genre,
                'year': args.year
            }

    chapters = loadChapters(args.chapter_file)
    writeCUE(chapters, args.audio_file, args.cue_file, extras)
    print 'Output successfully written to {0}'.format(args.cue_file)
