#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib
import sys
import argparse
import re
import requests
import time


class SoundCloudDownload:

    def __init__(self, url, verbose, tags):
        self.url = url
        self.verbose = verbose
        self.tags = tags
        self.download_progress = 0
        self.current_time = time.time()
        self.titleList = []
        self.streamURLlist = self.getStreamURLlist(self.url)

    def getStreamURLlist(self, url):
        r = requests.get("http://api.soundcloud.com/resolve.json?url={0}&client_id=YOUR_CLIENT_ID".format(url))
        streamList = []
        # Try to get the tracks in the playlist
        try:
            tracks = r.json()['tracks']
        # If this isn't a playlist, just make a list of
        # a single element (the track)
        except:
            tracks = [r.json()]
        for track in tracks:
            waveform_url = track['waveform_url']
            self.titleList.append(self.getTitleFilename(track['title']))
            regex = re.compile("\/([a-zA-Z0-9]+)_")
            r = regex.search(waveform_url)
            stream_id = r.groups()[0]
            streamList.append("http://media.soundcloud.com/stream/{0}".format(stream_id))
        return streamList

    def downloadSongs(self):
        for title, streamURL in zip(self.titleList, self.streamURLlist):
            filename = "{0}.mp3".format(title.encode('utf-8'))
            sys.stdout.write("\nDownloading: {0}\n".format(filename))
            try:
                ''' Support thai lang '''
                filename, headers = urllib.urlretrieve(url=streamURL, filename=filename.decode('utf-8').encode('tis-620'), reporthook=self.report)
                # reset download progress to report multiple track download progress correctly
                self.download_progress = 0
            except ArithmeticError:
                print "ERROR: Author has not set song to streamable, so it cannot be downloaded"

    def report(self, block_no, block_size, file_size):
        self.download_progress += block_size
        if int(self.download_progress / 1024 * 8) > 1000:
            speed = "{0} Mbps".format(round((self.download_progress / 1024 / 1024 * 8) / (time.time() - self.current_time), 2))
        else:
            speed = "{0} Kbps".format(round((self.download_progress / 1024 * 8) / (time.time() - self.current_time), 2))
        rProgress = round(self.download_progress/1024.00/1024.00, 2)
        rFile = round(file_size/1024.00/1024.00, 2)
        percent = round(100 * float(self.download_progress)/float(file_size))
        sys.stdout.write("\r {3} ({0:5.2f}/{1:.2f}MB): {2:5.2f}%".format(rProgress, rFile, percent, speed))
        sys.stdout.flush()

        ## Convenience Methods
    def getTitleFilename(self, title):
        return title


if __name__ == "__main__":
    if (int(requests.__version__[0]) == 0):
        print "Your version of Requests needs updating\nTry: '(sudo) pip install -U requests'"
        sys.exit()

    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
                        "-v",
                        "--verbose",
                        help="increase output verbosity",
                        action="store_true"
                        )
    parser.add_argument(
                        "-t",
                        "--id3tags",
                        help="add id3 tags",
                        action="store_true"
                        )
    parser.add_argument("SOUND_URL", help="Soundcloud URL")
    args = parser.parse_args()
    verbose = bool(args.verbose)
    tags = bool(args.id3tags)

    download = SoundCloudDownload(args.SOUND_URL, verbose, tags)
    download.downloadSongs()
