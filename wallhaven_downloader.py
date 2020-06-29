#!/usr/bin/env python
"""Downloads and sets a random wallpaper from wallhaven.cc"""

# Requires python-gobject, python-beautifulsoup4

import os
import sys
import re
import random
import urllib.request
from argparse import ArgumentParser
from bs4 import BeautifulSoup
from gi.repository import Gio

USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (Khtml, like Gecko) Chrome/35.0.1916.47 Safari/537.36'

def parse_args():
    """
    Parse arguments passed to the script.
    """
    wallpaper_directory = '/home/jonas/Pictures/script_wallpapers/'

    parser = ArgumentParser()
    parser.add_argument('-t', '--type', dest='type', help='Select the run type, local or download.')
    parser.add_argument('-d', '--dir', dest='dir', help='Overrides the default wallpaper directory for saving and randomizing using local.')

    args = parser.parse_args()
    if args.type not in ('download', 'local'):
        parser.print_help()
        sys.exit(1)
    if args.dir:
        wallpaper_directory = args.dir
    return args.type, wallpaper_directory


class WallhavenDownloader:

    def __init__(self, wallpaper_dir):
        self.random_url = 'https://alpha.wallhaven.cc/search?q=&categories=111&purity=111&ratios=32x9&sorting=random&order=desc'
        self.wallpaper_url = ''
        self.wallpaper_path = ''
        self.wallpaper_dir = wallpaper_dir

    def set_online_wallpaper(self):
        self._get_random_wallpaper()
        self._download_random_wallpaper()
        self._set_wallpaper()

    def set_local_wallpaper(self):
        self._get_local_wallpaper()
        self._set_wallpaper()

    def _get_random_wallpaper(self):
        """Downloads a random wallpaper from wallhaven.cc to the selected wallpaper directory"""
        wallpaper_list = []

        request = urllib.request.Request(self.random_url, data=None,
                                         headers={'User-Agent': USER_AGENT})
        resource = urllib.request.urlopen(request)
        if resource.getcode() != 200:
            sys.exit(1)

        soup = BeautifulSoup(resource.read(), 'html.parser')
        pattern = re.compile(r'^https:\\/\\/alpha\\.wallhaven\\.cc\\/wallpaper\\/([0-9]+)$')
        for link in soup.find_all('a'):
            link = link.get('href')
            if link is not None:
                match = pattern.match(link)
                if match is not None:
                    wallpaper_list.append(match.group(1))

        self.wallpaper_url = random.choice(wallpaper_list)

    def _download_random_wallpaper(self):
        """Downloads the selected random wallpaper"""
        wallpaper_formats = ['jpg', 'png', 'jpeg', 'bmp']

        for counter, file_ext in enumerate(wallpaper_formats):
            try:
                request = urllib.request.Request(f'https://wallpapers.wallhaven.cc/wallpapers/full/wallhaven-{self.wallpaper_url}.{file_ext}',
                                                 data=None, headers={'User-Agent': USER_AGENT})
                wallpaper_path = f'{self.wallpaper_dir}wallhaven-{self.wallpaper_url}.{file_ext}'
                resource = urllib.request.urlopen(request)
                if resource.getcode() == 200:
                    break
            except:
                if counter == len(wallpaper_formats):
                    sys.exit()
                else:
                    continue

        output = open(wallpaper_path, 'wb')
        output.write(resource.read())
        output.close()

        return wallpaper_path

    def _set_wallpaper(self):
        """Change the wallpaper to the one specified in the argument path"""
        pic_dconf_uri = 'org.gnome.desktop.background'
        settings = Gio.Settings.new(pic_dconf_uri)
        settings.set_string('picture-uri', f'file://{self.wallpaper_path}')

    def _get_local_wallpaper(self):
        """Picks a random local wallpaper and returns the filepath"""
        papers = []
        for filename in os.listdir(self.wallpaper_dir):
            papers.append(filename)
        self.wallpaper_path = f'{self.wallpaper_dir}{random.choice(papers)}'


if __name__ == '__main__':
    runtype, wallpaper_directory = parse_args()
    wallhaven_downloader = WallhavenDownloader(wallpaper_directory)
    if runtype == 'download':
        wallhaven_downloader.set_online_wallpaper()
    elif runtype == 'local':
        wallhaven_downloader.set_local_wallpaper()
