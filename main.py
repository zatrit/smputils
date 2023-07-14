#!/bin/python3
from argparse import ArgumentParser, Action


# https://stackoverflow.com/q/52132076/12245612
class SplitArgs(Action):
    def __call__(self, parser, namespace, values: str, option_string=None):
        setattr(namespace, self.dest, values.split(','))


def main():
    from smputils import config, run_config

    parser = ArgumentParser()
    parser.set_defaults(tasks=[])
    parser.add_argument('-t', '--tasks', action=SplitArgs, dest='tasks')
    parser.add_argument('-c', '--config', default='smputils.toml')

    args = parser.parse_args()
    config.init(__file__)
    _config = config.parse_config(args.config)

    try:
        run_config(_config, args.tasks)
    except AssertionError as err:
        print(err)


if __name__ == '__main__':
    main()
