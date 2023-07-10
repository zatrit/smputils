from typing import Any
from smputils.tasks import action


@action
def configure_server(config, deps: dict[str, Any]):
    props_file = config.get('props', 'server.properties')

    with open(props_file, 'r') as file:
        props = {}

        for line in (l.rstrip('\n\r') for l in file if not l.startswith('#')):
            key, value = line.split('=', 1)
            props[key] = value

    def update_property(key, value):
        props[key] = value
        print(key, value, sep=' = ')

    if merge := deps.get('merge'):
        print('PLEASE, UPLOAD YOUR RESOURCE PACK FROM', merge.path, 'TO ANY FILE HOSTING.')
        update_property('resource-pack-sha1', merge.sha1)

    with open(props_file, 'w') as file:
        for key, value in props.items():
            file.write('='.join((key, value)) + '\n')

    return props