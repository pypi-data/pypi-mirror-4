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
CHUNK_SIZE = 1024*128 # 128 KB

def video_key(video):
    bitrate = 0
    if video.find("videoBitrate") is not None:
        bitrate = int(video.videoBitrate.text)

    return (
        bitrate,
        video.find("facets") is not None and any((f.text == "progressive" for f in video.facets.facet))
    )

def video_valid(video):
    return (video.url.text.startswith("http") and video.url.text.endswith(".mp4"))

def get_id(url):
    return int(re.search(r"[^0-9]*([0-9]+)[^0-9]*", url).group(1))

def format_mb(bytes):
    return "%.2f" % (bytes/(1024*1024))

def main():
    if len(sys.argv) == 1:
        urls = sys.stdin.readlines()
    else:
        urls = sys.argv[1:]

    return 0 if all(list(map(video_dl, urls))) else 1

def video_dl(url):
    xml = objectify.fromstring(urllib.request.urlopen(XML_API % get_id(url)).read())

    status = xml.status
    if status.statuscode.text != "ok":
        print("Error retrieving manifest:")
        print("  %s" % status.statuscode.text)
        print("  %s" % status.debuginfo.text)
        return False

    video = xml.video
    title = video.information.title.text
    print(title)
    print("  %s" % video.details.vcmsUrl.text)

    videos = [v for v in video.formitaeten.formitaet if video_valid(v)]
    videos.sort(key=video_key, reverse=True)

    for v in videos:
        try:
            video = urllib.request.urlopen(v.url.text)
        except urllib.error.HTTPError as e:
            if e.code in [403, 404]:
                print("HTTP status %i on %s" % (e.code, v.url.text))
                continue

            raise e

        basename, ext = os.path.splitext(os.path.basename(urllib.parse.urlparse(v.url.text).path))
        filename = "{title} ({basename}){ext}".format(title=title, basename=basename, ext=ext)

        print("Downloading %s" % filename)
        print("  from %s" % v.url.text)

        size = 0
        target_size = int(video.info()["Content-Length"].strip())

        with open(filename, "wb") as f:
            data = video.read(CHUNK_SIZE)
            while data:
                size += len(data)
                f.write(data)
                data = video.read(CHUNK_SIZE)
                
                sys.stdout.write(" "*40 + "\r")
                sys.stdout.write("  %s/%s MB – %0.2f %%\r" % (format_mb(size), format_mb(target_size), round((float(size) / target_size)*100, 2)))
                sys.stdout.flush()
    
        print()
        return True
    return False

if __name__ == "__main__":
    sys.exit(main())
