import shutil
from smputils import config
from smputils.tasks import action
from tempfile import mkdtemp
import atexit

tmp_dirs = []


@action
def create_tmpdir(_config: dict, *_):
    store_global = _config['store_global']
    tmp_dirs.append(tmp_dir := mkdtemp())
    print('Created temporary directory', tmp_dir)

    config.config_globals[store_global] = tmp_dir


def cleanup():
    for tmp_dir in tmp_dirs:
        shutil.rmtree(tmp_dir)


atexit.register(lambda *_: cleanup())