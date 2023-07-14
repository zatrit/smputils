from smputils.tasks import action
from smputils import config


@action
def std_input(_config: dict, *_):
    data = input(_config.get('msg', ''))
    config.config_globals[_config['dest']] = data