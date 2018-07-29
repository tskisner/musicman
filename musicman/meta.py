# Copyright (c) 2018 by the parties listed in the AUTHORS
# file.  All rights reserved.  Use of this source code is governed
# by a BSD-style license that can be found in the LICENSE file.

from __future__ import (absolute_import, division, print_function,
    unicode_literals)

import sys
import os
import re

import subprocess as sp


taglist = [
    "album",
    "artist",
    "albumartist",
    "song",
    "track",
    "tracks",
    "year"
]


format_suffix = {
    "flac" : "flac",
    "alac" : "m4a",
    "ogg" : "ogg",
    "mp3" : "mp3"
}

suffix_format = {
    "flac" : "flac",
    "m4a" : "alac",
    "ogg" : "ogg",
    "mp3" : "mp3"
}


def quote_safe(input):
    return input.replace('"', '\\"')


def sprun(com, input=None):
    stdin = None
    if input is not None:
        stdin = sp.PIPE
    out = None
    err = None
    with sp.Popen(com, stdin=stdin, stdout=sp.PIPE, stderr=sp.PIPE,
                  universal_newlines=True) as p:
        if input is None:
            out, err = p.communicate()
        else:
            print("writing to stdin: ", input)
            out, err = p.communicate(input=input)
    return out.splitlines(), err.splitlines()


def live_report(com, label):
    p = sp.Popen(com, stdout=sp.PIPE, stderr=sp.STDOUT, universal_newlines=True)
    for line in p.stdout:
        print("    {}|{}|{}: {}{}{}".format(clr.LMAGENTA, label, clr.ENDC, clr.LGRAY, line.splitlines()[0], clr.ENDC))
    return


def file_split(path):
    pat = re.compile(r"([0-9]+)\s+(.*)\.(\w+)?$")
    sufpat = re.compile(r".*\.(\w+)?$")
    mat = pat.match(path)
    track = None
    name = None
    suffix = None
    if mat is not None:
        track = int(mat.group(1))
        name = mat.group(2)
        suffix = mat.group(3)
    else:
        # Our file name is different- see if we can at least get the suffix.
        mat = sufpat.match(path)
        if mat is not None:
            suffix = mat.group(1)
    return track, name, suffix


def find_format(path):
    track, name, suffix = file_split(path)
    if suffix.lower() in suffix_format:
        return suffix_format[suffix.lower()]
    else:
        return None


def song_get_props(path, format):
    props = dict()
    for t in taglist:
        props[t] = None

    if format == "flac":
        com = list()
        com.extend(["metaflac", "--export-tags-to=-"])
        com.append(path)
        out, err = sprun(com)
        for line in out:
            f = line.split('=')
            if f[0] == "ALBUM":
                if len(f[1]) > 0:
                    props["album"] = f[1]
            elif f[0] == "ALBUMARTIST":
                if len(f[1]) > 0:
                    props["albumartist"] = f[1]
            elif f[0] == "ARTIST":
                if len(f[1]) > 0:
                    props["artist"] = f[1]
            elif f[0] == "TITLE":
                if len(f[1]) > 0:
                    props["song"] = f[1]
            elif f[0] == "TRACKNUMBER":
                try:
                    props["track"] = int(f[1])
                except:
                    # The track number was invalid
                    props["track"] = None
            elif f[0] == "TRACKTOTAL":
                try:
                    props["tracks"] = int(f[1])
                except:
                    props["tracks"] = None
            elif f[0] == "DATE":
                if len(f[1]) > 0:
                    props["year"] = f[1]

    elif format == "alac":
        repat = {
            "song" : re.compile(r'.*Name:\s+"(.*)"$'),
            "artist" : re.compile(r'.*Artist:\s+"(.*)"$'),
            "album" : re.compile(r'.*Album:\s+"(.*)"$'),
            "albumartist" : re.compile(r'.*Album Artist:\s+"(.*)"$'),
            "tracks" : re.compile(r'.*Track:\s+(\d+) of (\d+)$')
        }
        com = list()
        com.extend(["mp4info"])
        com.append(path)
        out, err = sprun(com)
        for line in out:
            for k, v in repat.items():
                m = v.match(line)
                if m is not None:
                    if k == "tracks":
                        props["track"] = int(m.group(1))
                        props["tracks"] = int(m.group(2))
                    else:
                        props[k] = m.group(1)
                    break

    elif format == "ogg":

    elif format == "mp3":
        pass

    return props


def song_set_props(path, format, props):
    if format == "flac":
        metakeys = {
            "album" : "ALBUM",
            "artist" : "ARTIST",
            "albumartist" : "ALBUMARTIST",
            "song" : "TITLE",
            "track" : "TRACKNUMBER",
            "tracks" : "TRACKTOTAL",
            "year" : "DATE"
        }
        com = list()
        com.extend(["metaflac", "--remove-all-tags", "--import-tags-from=-"])
        com.append(path)
        print(" ".join(com))
        incom = ""
        for t in taglist:
            if props[t] is not None:
                incom = '{}{}={}\n'.format(incom, metakeys[t], props[t])
        out, err = sprun(com, input=incom)
        if len(err) > 0:
            print("\n".join(err), flush=True)

    elif format == "alac":
        metakeys = {
            "album" : "-A",
            "artist" : "-a",
            "albumartist" : "-R",
            "song" : "-s",
            "track" : "-t",
            "tracks" : "-T",
            "year" : "-y"
        }
        com = list()
        com.extend(["mp4tags"])
        for t in taglist:
            if props[t] is not None:
                if (t == "track") or (t == "tracks"):
                    com.append('{} {}'.format(metakeys[t], props[t]))
                else:
                    com.append('{} "{}"'.format(metakeys[t], props[t]))
        com.append(path)
        out, err = sprun(com)
        if len(err) > 0:
            print("\n".join(err), flush=True)

    elif format == "ogg":
        pass
    elif format == "mp3":
        pass

    return


def check_replace(props, key, val):
    if val is None:
        return
    if props[key] is None:
        props[key] = val
    else:
        if props[key] != val:
            print("WARNING:  Use metadata '{}' for key '{}' instead of '{}'"\
                .format(props[key], key, val))
    return


def album_props(albumdir):
    artistdir, album = os.path.split(albumdir)
    musicdir, artist = os.path.split(artistdir)
    maxtrack = 0
    songs = list()
    for root, dirs, files in os.walk(albumdir):
        for f in files:
            track, name, suffix = file_split(f)
            if suffix.lower() in suffix_format:
                # this is a song file
                format = suffix_format[suffix.lower()]
                songs.append( (track, name, format, os.path.join(root, f)) )
                if track is None:
                    maxtrack += 1
                else:
                    if track > maxtrack:
                        maxtrack = track
        break

    asongs = list()
    for track, name, format, raw in songs:
        # If any metadata is missing, get it from the filename.
        songprops = song_get_props(os.path.join(albumdir, raw), format)
        check_replace(songprops, "album", album)
        check_replace(songprops, "albumartist", artist)
        check_replace(songprops, "song", name)
        check_replace(songprops, "track", track)
        check_replace(songprops, "tracks", maxtrack)

        # artist is a special case, since it might be different for each song
        if songprops["artist"] is None:
            songprops["artist"] = artist

        asongs.append( (raw, format, songprops) )

    # Does the song metadata for artist and album contradict the filesystem
    # path?  If so, check that all songs agree, and then use the correct
    # and consistent values.

    check_album = asongs[0][2]["album"]
    if check_album != album:
        agree = True
        for sng in asongs:
            if sng[2]["album"] != check_album:
                agree = False
                break
        if agree:
            print("WARNING:  overriding filesystem album '{}' with metadata value '{}'".format(album, check_album))
            album = check_album

    check_artist = asongs[0][2]["albumartist"]
    if check_artist != artist:
        agree = True
        for sng in asongs:
            if sng[2]["albumartist"] != check_artist:
                agree = False
                break
        if agree:
            print("WARNING:  overriding filesystem album artist '{}' with metadata value '{}'".format(artist, check_artist))
            artist = check_artist

    return album, artist, asongs


if __name__ == "__main__":
    musicdir = sys.argv[1]
    mdir = os.path.abspath(musicdir)
    allartist = list()
    for root, dirs, files in os.walk(mdir):
        for d in dirs:
            allartist.append(d)
        break
    for art in allartist:
        artistdir = os.path.join(mdir, art)
        for root, dirs, files in os.walk(artistdir):
            for d in dirs:
                albumdir = os.path.join(artistdir, d)
                album, artist, songs = album_props(albumdir)
                print("Test {}:".format(albumdir))
                print("  album = {}".format(album))
                print("  albumartist = {}".format(artist))
                print("  songs:")
                for sngpath, sngformat, sngprops in songs:
                    print("    {} ({})".format(sngpath, sngformat))
                    for t in taglist:
                        print("    {} = {}".format(t, sngprops[t]))
            break
