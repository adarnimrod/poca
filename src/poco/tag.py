# -*- coding: utf-8 -*-

# Copyright 2010-2017 Mads Michelsen (mail@brokkr.net)
# This file is part of Poca.
# Poca is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.

"""Editing metadata on music files"""

import mutagen

from poco.outcome import Outcome


def tag_audio_file(settings, sub, entry):
    '''Metdata tagging using mutagen'''
    id3v1_dic = {'yes': 0, 'no': 2}
    id3v1 = id3v1_dic[settings.id3removev1.text]
    id3v2 = int(settings.id3v2version)
    frames = sub.xpath('./metadata/*')
    audio = mutagen.File(entry['poca_abspath'])
    if audio is None:
        return Outcome(False, 'Invalid file type')
    if audio.tags is None:
        audio.add_tags()
    if isinstance(audio, mutagen.mp3.MP3):
        if id3v2 == 3:
            audio.tags.update_to_v23()
        elif id3v2 == 4:
            audio.tags.update_to_v24()
        audio.save(v1=id3v1, v2_version=id3v2)
        audio = mutagen.File(entry['poca_abspath'], easy=True)
    if isinstance(audio, mutagen.mp3.EasyMP3):
        overrides = [(override.tag, override.text) for override in frames
                     if override.tag in audio.tags.valid_keys.keys()]
    else:
        overrides = [(override.tag, override.text) for override in frames]
    #if isinstance(audio, mutagen.oggvorbis.OggVorbis):
    #    pass
    #if isinstance(audio, mutagen.oggopus.OggOpus):
    #    pass
    #if isinstance(audio, mutagen.flac.FLAC):
    #    pass
    for override in overrides:
        audio[override[0]] = override[1]
    if isinstance(audio, mutagen.mp3.EasyMP3):
        audio.save(v1=id3v1, v2_version=id3v2)
    else:
        audio.save()
    return Outcome(True, 'Metadata successfully updated')
