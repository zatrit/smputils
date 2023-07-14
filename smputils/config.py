ConfigDef = str | dict
GLOBAL_SECTION = 'globals'
LOCAL_SECTION = 'locals'
config_globals = {}


def parse_config(config: ConfigDef, root: str = '.'):
    import tomllib
    from os.path import join

    vars = dict(**config_globals)
    vars.setdefault('config_root', root)

    if isinstance(config, str):
        with open(join(root, config), 'rb') as file:
            config = tomllib.load(file)
    fill_vars(config, vars)
    return config


def fill_vars(target, vars: dict):
    if isinstance(target, str):
        return target.format(**vars)
    elif isinstance(target, dict):
        for key, value in target.items():
            target[key] = fill_vars(value, vars)
            if key == GLOBAL_SECTION:
                config_globals.update(value)
            if key in (LOCAL_SECTION, GLOBAL_SECTION):
                vars.update(value)
    elif isinstance(target, list):
        for i, value in enumerate(target):
            target[i] = fill_vars(value, vars)

    return target


def init(main_path):
    from os.path import pardir, join, abspath

    config_globals['script_root'] = abspath(join(main_path, pardir))