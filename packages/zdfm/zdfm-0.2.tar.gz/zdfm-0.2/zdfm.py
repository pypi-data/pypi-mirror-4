#!/usr/bin/env python3

import argparse
import urllib.request
import urllib.error
import urllib.parse
import os.path
import sys
import re

from lxml import objectify

XML_API = "http://www.zdf.de/ZDFmediathek/xmlservice/web/beitragsDetails?id=%i"
CHUNK_SIZE = 1024*1024*2 # 2 MB

def video_key(video):
    return (
        int(video.videoBitrate.text),
        video.find("facets") is not None and any((f.text == "progressive" for f in video.facets.facet))
    )

def get_id(url):
    try:
        return int(url)
    except ValueError:
        pass

    return int(re.search(r"beitrag/video/([0-9]+)/", url).group(1))

def main():
    if len(sys.argv) == 1:
        print("Need video ID/URL")
        return 1

    xml = objectify.fromstring(urllib.request.urlopen(XML_API % get_id(sys.argv[-1])).read())

    status = xml.status
    if status.statuscode.text != "ok":
        print("Error retrieving manifest:")
        print("  %s" % status.statuscode.text)
        print("  %s" % status.debuginfo.text)
        return 2

    video = xml.video

    print(video.information.title.text)
    print("  %s" % video.details.vcmsUrl.text)

    videos = [v for v in video.formitaeten.formitaet if v.url.text.startswith("http")]
    videos.sort(key=video_key, reverse=True)

    for v in videos:
        try:
            video = urllib.request.urlopen(v.url.text)
        except urllib.error.HTTPError as e:
            if e.code in [403, 404]:
                print("HTTP status %i on %s" % (e.code, v.url.text))
                continue

            raise e

        basename = os.path.basename(urllib.parse.urlparse(v.url.text).path)

        print("Downloading %s" % basename)
        print("  from %s" % v.url.text)

        size = 0
        with open(basename, "wb") as f:
            data = video.read(CHUNK_SIZE)
            while data:
                size += len(data)
                f.write(data)
                data = video.read(CHUNK_SIZE)
                sys.stdout.write(".")
                sys.stdout.flush()

        print("\nFinished (%.2f MB)." % (size/(1024*1024)))

        break

    return 0

if __name__ == "__main__":
    sys.exit(main())