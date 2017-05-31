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


def tag_audio_file(settings, sub, jar, entry):
    '''Metdata tagging using mutagen'''
    id3v1_dic = {'yes': 0, 'no': 2}
    id3v1 = id3v1_dic[settings.id3removev1.text]
    id3v2 = int(settings.id3v2version)
    tracks = sub.find('./track_numbering')
    tracks = tracks.text if tracks else 'no'
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
    if tracks == 'yes' or (tracks == 'if missing' and not
                           'tracknumber' in audio):
        track_no = jar.track_no if hasattr(jar, 'track_no') else 0
        track_no += 1
        jar.track_no = track_no
        jar.save()
        track_str = str(track_no).rjust(3, '0')
        audio['tracknumber'] = track_str
        # note: we save the jar before we know if tagging is succesful
        # could mean skipped track numbers
    if isinstance(audio, mutagen.mp3.EasyMP3):
        audio.save(v1=id3v1, v2_version=id3v2)
    else:
        audio.save()
    return Outcome(True, 'Metadata successfully updated')
