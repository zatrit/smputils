# https://stackoverflow.com/a/29855240/12245612
def import_file(full_name, path):
    from importlib import util

    spec = util.spec_from_file_location(full_name, path)
    assert spec
    assert spec.loader
    mod = util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod
