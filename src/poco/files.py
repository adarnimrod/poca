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
import re
import sys
import signal
import socket
import urllib.request
import urllib.error

from poco.outcome import Outcome


# download
class NoMoreBufferException(Exception):
    pass

class TimesUpException(Exception):
    pass

def download_block(u, f, block_size):
    '''Download until there's no more to download'''
    buffer = u.read(block_size)
    if not buffer:
        raise NoMoreBufferException("No more to download")
    f.write(buffer)

def handler(signum, frame):
    raise TimesUpException("Download timed out")

def download_file(url, file_path):
    '''Download function with block time outs'''
    try:
        u = urllib.request.urlopen(url)
    except urllib.error.HTTPError as e:
        return Outcome(False, str(e))
    except socket.error as e:
        return Outcome(False, str(e))

    signal.signal(signal.SIGALRM, handler)
    f = open(file_path, "wb")

    block_size = 8192
    while True:
        signal.alarm(90)
        try:
            download_block(u, f, block_size)
        except NoMoreBufferException as e:
            outcome = Outcome(True, str(e))
            f.close()
            break
        except TimesUpException as e:
            outcome = Outcome(False, str(e))
            f.close()
            del_outcome = delete_file(file_path)
            break
        except KeyboardInterrupt:
            f.close()
            del_outcome = delete_file(file_path)
            sys.exit()

    signal.alarm(0)
    signal.signal(signal.SIGALRM, signal.SIG_DFL)

    return outcome

def download_img_file(url, sub_dir):
    extension = os.path.splitext(url)[1]
    extension = re.match('\.[a-zA-Z]+', extension)
    if extension:
        extension = extension.group()
    else:
        extension = '.jpg'
    file_path = os.path.join(sub_dir, 'cover' + extension)
    return download_file(url, file_path)

# delete
def delete_file(file_path):
    '''Deletes a file'''
    try:
        os.remove(file_path)
        return Outcome(True, file_path + ': File was successfully deleted')
    except OSError as e:
        return Outcome(False, file_path + ': ' + str(e))

# permissions check
def check_path(check_dir):
    '''Create a directory'''
    if os.path.isdir(check_dir):
        if os.access(check_dir, os.W_OK):
            return Outcome(True, check_dir + ': Dir exists already.')
        else:
            return Outcome(False, check_dir + ': Lacks permissions to dir.')
    try:
        os.makedirs(check_dir)
        return Outcome(True, check_dir + ': Dir was successfully created.')
    except OSError as e:
        return Outcome(False, check_dir + ': Dir could not be created.')

