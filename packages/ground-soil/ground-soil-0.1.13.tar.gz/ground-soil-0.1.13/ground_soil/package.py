import os
import threading
import xmlrpclib
from ground_soil.console.color import Colors, color


def check_update(app_name, local_version_string, data_folder, quiet=False):
    local_version_file_path = os.path.join(data_folder, 'pypi-version')

    def check_update_core():
        pypi = xmlrpclib.ServerProxy('http://pypi.python.org/pypi')
        with open(local_version_file_path, 'w') as f:
            try:
                pypi_version = pypi.package_releases(app_name)[0]
                f.write(pypi_version)
            except (IndexError, ValueError):
                f.write('')
    thread1 = threading.Thread(target=check_update_core)
    thread1.start()

    if os.path.exists(local_version_file_path):
        with open(local_version_file_path, 'r') as f:
            try:
                version_string = f.read()
                pypi_version = tuple(map(lambda x: int(x), version_string.split('.')))
                local_version = tuple(map(lambda x: int(x), local_version_string.split('.')))
                if pypi_version > local_version:
                    msg = '{name} {ver} has been released, please update it.'.format(name=app_name, ver=version_string)
                    print color(msg, Colors.YELLOW)
                    print ''
                    return 1
                else:
                    raise ValueError
            except ValueError:
                pass

    if not quiet:
        print color(
            '{name} is update to date. (version={ver})'.format(name=app_name, ver=local_version_string), Colors.GREEN)
    return 0
