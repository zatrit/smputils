from os import path, makedirs
from smputils.tasks import action
from ftplib import FTP
from fnmatch import fnmatch


def init_ftp(config: dict):
    passwd = config.get('passwd', '')
    login = config.get('login', '')
    server = config['server']

    remote_root = config.get('remote_root', '/')

    ftp = FTP(server)
    ftp.login(user=login, passwd=passwd)
    ftp.cwd(remote_root)

    return ftp


def ftp_query_files(ftp: FTP, files: list):
    for group in files:
        patt = group.get('pattern')
        root = group.get('root', './')
        local_root = group.get('local_root', root)
        makedirs(local_root, exist_ok=True)
        for name, attrs in \
            ((name, attrs) for name, attrs
             in ftp.mlsd(root) if fnmatch(name, patt)):
            remote = path.join(root, name)
            local = path.join(local_root, name)

            yield remote, local, attrs


@action
def ftp_download(config: dict, *_):
    files = config.get('files', [])
    ftp = init_ftp(config)

    for remote, local, attrs in ftp_query_files(ftp, files):
        if attrs['type'] != 'file':
            continue
        print('Downloading', remote)

        with open(local, 'wb') as file:
            ftp.retrbinary('RETR ' + remote, file.write)


@action
def ftp_upload(config: dict, *_):
    from glob import iglob

    files = config.get('files', [])
    ftp = init_ftp(config)

    for group in files:
        local_root = group['local_root']
        remote_root = group['remote_root']
        pattern = group['pattern']

        for _path in iglob(pattern, root_dir=local_root):
            local = path.join(local_root, _path)
            remote = path.join(remote_root, _path)

            if path.isdir(local):
                ftp.mkd(remote)
            elif path.isfile(local):
                with open(local, 'rb') as file:
                    ftp.storbinary('STOR ' + remote, file)