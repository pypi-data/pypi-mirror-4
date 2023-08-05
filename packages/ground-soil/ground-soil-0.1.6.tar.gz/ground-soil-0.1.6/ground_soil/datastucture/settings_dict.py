import types
from six import callable
from ground_soil.datastucture.modules import dict_from_module_attr, load_module_as_dict


class SettingsDict(dict):
    def __init__(self, *setting_components, **setting_patches):
        super(SettingsDict, self).__init__()

        for setting_component in (setting_components + (setting_patches,)):
            if isinstance(setting_component, (str, unicode)):
                settings = load_module_as_dict(setting_component, lambda key: key.isupper())
            elif isinstance(setting_component, types.ModuleType):
                settings = dict_from_module_attr(setting_component, lambda key: key.isupper())
            elif isinstance(setting_component, dict):
                settings = dict([(key, value) for key, value in setting_component.items() if key.isupper()])
            else:
                continue

            if settings is not None:
                self.update(settings)

    def get(self, *args):
        if len(args) == 1:
            return self[args[0]]
        elif len(args) == 2:
            try:
                return self[args[0]]
            except KeyError:
                return args[1]
        else:
            raise TypeError('get() takes exactly 1 or 2 arguments (%s given)' % len(args))

    def __getattr__(self, item):
        return self[item]

    def __getitem__(self, item):
        if item in self:
            target = super(SettingsDict, self).__getitem__(item)
            return target() if callable(target) else target
        else:
            raise KeyError(item)
