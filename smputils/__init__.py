from .tasks import run_tasks, actions, Task
from .utils import import_file
from .config import parse_config


def run_config(config: dict, tasks: list = []):
    config_tasks = []
    raw_tasks = config.get('tasks', [])
    tasks_set = set(tasks)

    for mod, path in config.get('imports', {}).items():
        import_file(mod, path)

    for task in raw_tasks:
        task.setdefault('name', task['action'])
        task.setdefault('deps', {})

    tasks_dict = {t['name']: t for t in raw_tasks}

    for task in tasks_set.copy():
        task_deps(task, tasks_dict, tasks_set)

    for name, task in tasks_dict.items():
        action = task['action']
        force_index = task.get('force_index', -1)

        if tasks_set and (name not in tasks_set):
            continue

        action = actions[action]
        config_tasks.append(
            Task(name, action, task['deps'],
                 task.get('config', {}), force_index))

    run_tasks(config_tasks)


def task_deps(task: str, tasks: dict, target=set()):
    target.add(task)
    for dep in tasks[task]['deps'].values():
        task_deps(dep, tasks, target)
    return target
