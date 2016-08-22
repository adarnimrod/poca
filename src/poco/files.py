# -*- coding: utf-8 -*-
# Copyright 2010-2016 Mads Michelsen (mail@brokkr.net)
# except download function copyright PabloG 
# (http://stackoverflow.com/users/394/pablog) and Mads Michelsen 2015, 2016
# 
# This file is part of Poca.
# Poca is free software: you can redistribute it and/or modify it 
# under the terms of the GNU General Public License as published by 
# the Free Software Foundation, either version 3 of the License, 
# or (at your option) any later version.

import os
import shutil
import urllib.request, urllib.error, urllib.parse
from urllib.request import urlretrieve

import mutagen

from poco.id3v23_frames import frame_dic
from poco.output import Outcome


def check_path(check_dir):
    '''Create a directory'''
    if os.path.isdir(check_dir):
        if os.access(check_dir, os.W_OK):
            return Outcome(True, check_dir + ': Directory exists already.')
        else:
            return Outcome(False, check_dir + ': Lacks permissions to directory.')
    try:
        os.makedirs(check_dir)
        return Outcome(True, check_dir + ': Directory was successfully created.')
    except OSError as e:
        return Outcome(False, check_dir + ': Directory could not be created.')


def write_file(file_path, text):
    '''Writes a string to file. Currently specific to creating config file.'''
    try:
        wfile = open(file_path, mode='wt', encoding='utf-8')
        wfile.write(text)
        wfile.close()
        return Outcome(True, 'New config file successfully created')
    except IOError as e:
        return Outcome(False, file_path + ': ' + str(e))


def delete_file(file_path):
    '''Deletes a file'''
    # standardise on the dataunit being passed around?
    # this should be a entry not a filename
    try:
        os.remove(file_path)
        return Outcome(True, file_path + ': File was successfully deleted')
    except OSError as e:
        return Outcome(False, file_path + ': ' + str(e))

def download_audio_file(entry):
    '''Downloads one file'''
    try:
        dummy, response = urlretrieve(entry['poca_url'], entry['poca_abspath'])
        return Outcome(True, 'File was successfully downloaded')
    except urllib.error.HTTPError as e:
        return Outcome(False, "HTTPError: " + str(e))
    except IOError as e:
        return Outcome(False, "IOError: " + str(e))


def tag_audio_file(sets_dic, entry_dic, sub_dic):
    '''NOT IN CURRENT USE. Reintroducing id3 tagging using mutagen'''
    # get general metadata settings
    id3version_dic = {'2.3': 3, '2.4': 4}
    id3version = id3version_dic[sets_dic['metadata']['id3version']]
    id3v1_dic = {'yes': 0, 'no': 2}
    id3v1 = id3v1_dic[sets_dic['metadata']['removeid3v1']] 
    id3encoding = 0
    if sets_dic['metadata']['unicode'] == 'yes':
        id3encoding_dic = {3: 1, 4: 3}
        id3encoding = id3encoding_dic[id3version]
    # overwrite metadata in the present file 
    localfile = os.path.join(sub_dic['sub_dir'], entry_dic['filename'])
    file_extension = os.path.splitext(localfile)[1].lower()
    if file_extension != '.mp3':
        # outcome = ...
        return
    if 'metadata' not in sub_dic:
        # outcome = ...
        return
    try:
        id3tag = mutagen.id3.ID3(localfile)
    except mutagen.id3.ID3NoHeaderError:
        easytag = mutagen.File(localfile, easy=True)
        easytag.add_tags()
        easytag['title'] = os.path.basename(localfile).split('.')[0]
        easytag.save()
        id3tag = mutagen.id3.ID3(localfile)
    if id3version == 3:
        id3tag.update_to_v23()
    for override in sub_dic['metadata']:
        frame = frame_dic[override]
        ftext = sub_dic['metadata'][override]
        id3tag.add(frame(encoding=id3encoding, text=ftext))
        try:
            id3tag.save(v1=id3v1, v2_version=id3version)
        except UnicodeEncodeError:
            error = ('The metadata overrides contain Unicode characters '
            'but you have chosen a non-Unicode encoding.')
            suggest = ('Please change either your Unicode preference or '
            'your overrides')
            errors.errors(error, suggest)

