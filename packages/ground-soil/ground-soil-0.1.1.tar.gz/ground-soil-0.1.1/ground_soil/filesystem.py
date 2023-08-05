import json
import os
import re
import tempfile
from contextlib import contextmanager
from jinja2 import FileSystemLoader, Environment


@contextmanager
def temporary_directory(identifier='com.wantoto.ground-ground_soil', prefix=None, suffix=None):
    """Generate a temporary directory with identifier, usage, and name under system's temporary root.
    :param identifier: Bundle identifier or Java package
    :param prefix: prefix in the name of this temporary folder
    :param suffix: suffix in the name of this temporary folder
    :return: This is a context manager. It returns the path of the temporary directory
    """
    # Get temporary room
    os_temp_dir = os.path.join(tempfile.gettempdir(), identifier)
    if not os.path.exists(os_temp_dir):
        os.mkdir(os_temp_dir)
    # Make temporary folder in room
    path = tempfile.mkdtemp(prefix=(prefix or 'tmp'), dir=os_temp_dir, suffix=(suffix or ''))

    try:
        yield path
    finally:
        os.system('rm -rf %s' % path)


def rsync(source, destination, rsync_schema=None, rsync_argument='-rlpctzD', expand_to_destination=False):
    """Using rsync as cp or scp. Note both source and destination do not support ":" (colon)
    :param source:
        path of source. (local path or remote path like scp/rsync)
    :param destination:
        path of destination. (local path or remote path like scp/rsync)
    :param rsync_schema:
        rsync schema. if one of source and destination is remote path, we use ssh.
    :param rsync_argument:
        rsync schema. default is "-rlpctzD"
    :return
        composed rsync command
    """
    rsync = 'rsync %s' % rsync_argument

    if source.startswith('localhost:'):
        source = source.replace('localhost:', '')
    elif source.startswith('127.0.0.1:'):
        source = source.replace('127.0.0.1:', '')
    if expand_to_destination and os.path.isdir(source) and not source.endswith('/'):
        source += '/'

    if destination.startswith('localhost:'):
        destination = destination.replace('localhost:', '')
    elif destination.startswith('127.0.0.1:'):
        destination = destination.replace('127.0.0.1:', '')

    if (':' in source or ':' in destination) and rsync_schema is None:
        rsync_schema = 'ssh'

    if rsync_schema:
        rsync += ' -e "%s"' % rsync_schema

    rsync += ' %s %s' % (source, destination)

    return rsync


def render_file(file_path, context, optimize=False):
    """
    Render Jinja2-compatible templates with context
    :param file_path: The path of template file
    :param context: The context used to render the template
    :param optimize: Reduce empty line and strip
    :return: Rendered result
    """
    templates_folder, template_filename = os.path.split(file_path)
    env = Environment(loader=FileSystemLoader(templates_folder))
    t = env.get_template(template_filename)
    result = t.render(**context)
    if optimize:
        result = re.sub(r'( *\n){2,}', '\n\n', result.strip()) + '\n'
    return result


def edit_file(file_path, reader=None, writer=None, editor=None):
    if editor is None:
        return
    if reader is None:
        reader = lambda x: json.loads(x)
    if writer is None:
        writer = lambda x: json.dumps(x, separators=(',', ':'))

    with open(file_path, 'r') as f:
        content = reader(f.read())

    content = editor(content)

    tmp_file = '%s.bak' % file_path
    with open(tmp_file, 'w') as f:
        f.write(writer(content))

    os.system('mv %s %s' % (tmp_file, file_path))
