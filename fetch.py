from os.path import basename, join

from smputils.tasks import action


def fetch_url(params: dict[str, str], target_dir: str):
    import requests

    url = params['url']
    
    print('Downloading', url)

    response = requests.get(url)
    path = join(target_dir, params.get('filename', basename(url)))

    with open(path, 'wb') as file:
        file.write(response.content)


def fetch_spiget(params: dict[str, str], target_dir: str):
    resource_id = params['resource_id']
    params['url'] = f'https://api.spiget.org/v2/resources/{resource_id}/download'
    return fetch_url(params, target_dir)


def copy(params: dict[str, str], target_dir: str):
    from shutil import copytree, copy
    from os.path import isfile, isdir

    source = params['source']
    path = join(target_dir, params.get('filename', basename(source)))

    print('Copying', source)

    if isfile(source):
        copy(source, path)
    elif isdir(source):
        copytree(source, path)
    else:
        print(source, 'is not file.')


sources = {'url': fetch_url, 'copy': copy, 'spiget': fetch_spiget}


@action
def fetch(config: dict, *_):
    from os import makedirs

    files = config.get('files', [])
    target_dir = config['target_dir']

    makedirs(target_dir, exist_ok=True)

    for file in files:
        source = sources[file['type']]
        source(file, target_dir)
