from dataclasses import dataclass
from typing import Callable, Any

TaskFunc = Callable[[dict, dict], Any]


@dataclass
class TaskAction:
    func: TaskFunc
    name: str
    deps: dict[str, type]


@dataclass
class Task:
    name: str
    action: TaskAction
    deps: dict[str, str]
    config: dict


actions: dict[str, TaskAction] = {}


def action(fn=None, *, deps: dict[str, type] = dict()):
    def _action(fn):
        name = fn.__name__
        for key, value in deps.items():
            deps[key] = value or type(value)
        actions[name] = TaskAction(fn, name, deps)
        return fn
    return _action(fn) if fn else _action


# https://codereview.stackexchange.com/q/239008
def kahn(graph: dict) -> list:
    in_degree = {u: sum(u in v for v in graph.values()) for u in graph}
    no_indegree_vertices = {vertex for vertex,
                            count in in_degree.items() if count == 0}

    topological_sort = []
    while no_indegree_vertices:
        vertex = no_indegree_vertices.pop()
        topological_sort.append(vertex)
        for neighbor in graph.get(vertex, []):
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                no_indegree_vertices.add(neighbor)

    assert len(topological_sort) == len(
        in_degree), 'Graph has cycles; It is not a directed acyclic graph.'

    return topological_sort


def run_tasks(tasks: list[Task]):
    graph = {t.name: list(t.deps.values()) for t in tasks}
    order = list(reversed(kahn(graph)))
    tasks = sorted(tasks, key=lambda t: order.index(t.name))
    result = {}

    for task in tasks:
        print('=> Running task', task.name)

        action = task.action
        deps_input = {a: result[b] for a, b in task.deps.items()}

        in_keys, exc_keys = set(deps_input), set(action.deps)
        assert exc_keys.issubset(
            in_keys), f'Not all dependencies for {task.name} are satisfied. Expected: {exc_keys}, given: {in_keys}'

        for key, value in deps_input.items():
            if not (dep_type := action.deps.get(key, None)):
                continue
            assert isinstance(
                value, dep_type), f'{key} must be instance of {dep_type.__name__}'

        result[task.name] = action.func(task.config, deps_input)
