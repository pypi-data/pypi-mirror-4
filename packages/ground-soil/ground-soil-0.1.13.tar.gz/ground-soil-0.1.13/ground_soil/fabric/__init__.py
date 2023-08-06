import ast
import json
from fabric.api import local, prefix
from fabric.main import _escape_split

escape_split = _escape_split


def lsudo(command, capture=False):
    return local('sudo {command}'.format(command=command), capture=capture)


def virtual_env(venv_path):
    return prefix('source {path}/bin/activate'.format(path=venv_path))


def eval_arg(raw_value, is_json=False):
    if is_json:
        try:
            return json.loads(raw_value)
        except ValueError:
            return raw_value
    else:
        try:
            return ast.literal_eval(raw_value)
        except (SyntaxError, ValueError):
            return raw_value


def eval_args(args):
    return map(eval_arg, args)


def eval_kwargs(kwargs):
    return dict(map(lambda x: (x[0], eval_arg(x[1])), kwargs.items()))
