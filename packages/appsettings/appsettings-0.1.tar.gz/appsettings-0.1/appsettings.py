import os

import yaml


class SettingsStruct(object):
    """
    A container for dot-notated access to a dictionary of config data like
    you'd get from parsing a safe yaml file.
    """
    def __init__(self, **entries):
        for k, v in entries.items():
            self.__dict__[k] = self.structify(v)

    @classmethod
    def structify(cls, item):
        """
        Convert possibly-nested YAML-safe type into dot-notated struct.

        Dictionaries are made into objects, lists are checked for dictionaries,
        and all other types are passed through.
        """
        if isinstance(item, dict):
            return cls(**item)

        if isinstance(item, list):
            return [cls.structify(i) for i in item]

        return item


def read(env_var='APP_SETTINGS_YAML'):
    """
    Given the name of an environment variable that should contain a path to a
    yaml file with a dictionary full of settings, return a SettingsStruct that
    provides dot-style access to those settings.
    """
    return SettingsStruct(**yaml.safe_load(open(os.environ[env_var])))


def unstrict_read(env_var='APP_SETTINGS_YAML'):
    """
    Just like appsettings.read(), but don't choke on a missing env var or file.
    Return an empty struct in those cases.
    """
    try:
        return read(env_var)
    except (KeyError, IOError):
        # IF the env var isn't set, or the file doesn't exist, just return an
        # empty dict.
        return SettingsStruct(**{})
