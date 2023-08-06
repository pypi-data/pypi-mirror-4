import imp
import os


def dict_from_module_attr(module_object, key_filter=None):
    if key_filter is None:
        key_filter = lambda x: True

    result = {}
    for attribute in dir(module_object):
        if key_filter(attribute):
            result[attribute] = getattr(module_object, attribute)
    return result


def load_module_as_dict(path, key_filter=None):
    if not os.path.exists(path):
        return {}

    file_name = os.path.split(os.path.splitext(path)[0])[1]
    module_object = imp.load_source(file_name, path)

    return dict_from_module_attr(module_object, key_filter)
