#!/usr/bin/env python3

import argparse
import urllib.request
import urllib.error
import urllib.parse
import os.path
import sys
import re
from xml.etree.ElementTree import fromstring

XML_API = "http://www.zdf.de/ZDFmediathek/xmlservice/web/beitragsDetails?id=%i"
CHUNK_SIZE = 1024*128 # 128 KB

def video_key(video):
    return (
        int(video.findtext("videoBitrate", "0")),
        any(f.text == "progressive" for f in video.iter("facet")),
    )

def video_valid(video):
    return (video.findtext("url").startswith("http") and video.findtext("url").endswith(".mp4"))

def get_id(url):
    return int(re.search(r"[^0-9]*([0-9]+)[^0-9]*", url).group(1))

def format_mb(bytes):
    return "%.2f" % (bytes/(1024*1024))

def video_dl(url):
    xml = fromstring(urllib.request.urlopen(XML_API % get_id(url)).read())

    status = xml.findtext("./status/statuscode")
    if status != "ok":
        print("Error retrieving manifest:")
        print("  %s" % status.statuscode.text)
        print("  %s" % status.debuginfo.text)
        return False

    video = xml.find("video")
    title = video.findtext("information/title")
    print(title)
    print("  %s" % video.findtext("details/vcmsUrl"))

    videos = sorted((v for v in video.iter("formitaet") if video_valid(v)), key=video_key, reverse=True)
    for v in videos:
        url = v.findtext("url")
        try:
            video = urllib.request.urlopen(url)
        except urllib.error.HTTPError as e:
            if e.code in [403, 404]:
                print("HTTP status %i on %s" % (e.code, url))
                continue
            raise e

        basename, ext = os.path.splitext(os.path.basename(urllib.parse.urlparse(url).path))
        filename = "{title} ({basename}){ext}".format(title=title, basename=basename, ext=ext)

        print("Downloading %s" % filename)
        print("  from %s" % url)

        size = 0
        target_size = int(video.info()["Content-Length"].strip())
        with open(filename, "wb") as f:
            data = video.read(CHUNK_SIZE)
            while data:
                size += len(data)
                f.write(data)
                data = video.read(CHUNK_SIZE)

                print("%s/%s MB – %0.2f %%" % (format_mb(size), format_mb(target_size), size/target_size*100), " "*10, end="\r")
        print()
        return True
    return False

def main():
    if len(sys.argv) == 1:
        urls = sys.stdin.readlines()
    else:
        urls = sys.argv[1:]

    return 0 if all(list(map(video_dl, urls))) else 1

if __name__ == "__main__":
    sys.exit(main())
