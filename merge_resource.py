#!/bin/python
import hashlib
from fnmatch import fnmatch
from itertools import filterfalse
from zipfile import ZipFile, ZIP_DEFLATED
from dataclasses import dataclass
from io import BytesIO

from smputils.tasks import action

COMP = ZIP_DEFLATED
exclude = []


def excluded(path):
    return any(map(lambda p: fnmatch(path, p), exclude))


class BaseReader:
    def __exit__(self, *_):
        pass

    def __enter__(self):
        return self


class ZIPReader(BaseReader):
    def __init__(self, file):
        self.zip = ZipFile(file)

    def __exit__(self, *_):
        self.zip.close()

    def copy(self, other: ZipFile):
        zip = self.zip
        for info in zip.infolist():
            if excluded(info.filename):
                continue

            try:
                other.getinfo(info.filename)
                print(info.filename, 'already exists, skipping')
                continue
            except:
                pass

            if info.is_dir():
                other.mkdir(info.filename)
            else:
                other.writestr(info, zip.read(info))


class DirReader(BaseReader):
    def __init__(self, dir: str):
        self.dir = dir

    def copy(self, other: ZipFile):
        import os
        from os.path import join
        for root, dirs, files in os.walk(self.dir):
            _root = root.removeprefix(self.dir)
            if excluded(_root):
                continue
            for dir in filterfalse(excluded, dirs):
                other.mkdir(join(_root, dir))
            for file in filterfalse(excluded, files):
                other.write(join(root, file), join(
                    _root, file), compress_type=COMP)


def url_source(params: dict[str, str]):
    import requests

    url = params['url']
    print('Connecting to', url)
    response = requests.get(url)
    return ZIPReader(BytesIO(response.content))


def file_source(params: dict[str, str]):
    path = params['patn']
    print('Reading', path)
    return ZIPReader(open(path, 'r'))


def dir_source(params: dict[str, str]):
    path = params['path']
    print('Reading', path)
    return DirReader(path)


sources = {'url': url_source, 'file': file_source, 'dir': dir_source}


@dataclass
class MergeResult:
    sha1: str
    path: str


@action
def merge_resource(config, *_) -> MergeResult:
    global exclude
    exclude = config.get('exclude', [])

    with open(config['output'], 'wb') as file,     ZipFile(file, 'w', compression=COMP) as zip:
        file.truncate(0)
        for _source in config.get('sources', []):
            source = sources[_source['type']]
            with source(_source) as reader:
                reader.copy(zip)

    BUF_SIZE = 65536

    sha1 = hashlib.sha1(usedforsecurity=False)

    with open(config['output'], 'rb') as file:
        while data := file.read(BUF_SIZE):
            sha1.update(data)

    print('\nSHA1:', _hash := sha1.hexdigest())

    return MergeResult(_hash, config['output'])
