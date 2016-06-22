# -*- coding: utf-8 -*-

"""
iniconfig
---------

A more convenient and practical approach to manage .ini files.
You can link a class property with an .ini file option and
delegating your management.

MIT license

See https://github.com/dmiro/iniconfig for more information
"""

try:
    from ConfigParser import ConfigParser #py2
except ImportError:
    from configparser import ConfigParser #py3
from ast import literal_eval
from collections import MutableMapping, MutableSequence


class SetterDict(MutableMapping, dict):

    def __init__(self, settermethod, dict_):
        super(SetterDict, self).__init__(dict_)
        self.__settermethod = settermethod

    def __getitem__(self, key):
        return dict.__getitem__(self, key)

    def __setitem__(self, key, value):
        dict.__setitem__(self, key, value)
        self.__settermethod(self)

    def __delitem__(self, key):
        dict.__delitem__(self, key)
        self.__settermethod(self)

    def __iter__(self):
        return dict.__iter__(self)

    def __len__(self):
        return dict.__len__(self)


class SetterList(MutableSequence, list):

    def __init__(self, settermethod, list_):
        super(SetterList, self).__init__(list_)
        self.__settermethod = settermethod

    def __getitem__(self, key):
        return list.__getitem__(self, key)

    def __setitem__(self, value):
        list.__setitem__(self, value)
        self.__settermethod(self)

    def __delitem__(self, key):
        list.__delitem__(self, key)
        self.__settermethod(self)

    def __len__(self):
        return list.__len__(self)

    def insert(self, index, object_):
        list.insert(self, index, object_)
        self.__settermethod(self)


class IniConfig(object):

    def __init__(self, filename):
        super(IniConfig, self).__init__()
        self.filename = filename
        self.config = ConfigParser()
        self.config.read(self.filename)

    def __save(self):
        with open(self.filename, 'wb') as configfile:
            self.config.write(configfile)

    @classmethod
    def iniproperty(cls, section, option, default):

        def getter(owner):
            if not owner.config.has_section(section):
                owner.config.add_section(section)
            if owner.config.has_option(section, option):
                literal = owner.config.get(section, option)
                value = literal_eval(literal)              # http://stackoverflow.com/a/16269302/2270217
            else:
                value = default
            if isinstance(value, dict):
                settermethod = lambda value: setter(owner, value)
                value = SetterDict(settermethod, value)
            if isinstance(value, list):
                settermethod = lambda value: setter(owner, value)
                value = SetterList(settermethod, value)
            return value

        def setter(owner, value):
            if not owner.config.has_section(section):
                owner.config.add_section(section)
            owner.config.set(section, option, str(value))  # http://stackoverflow.com/a/21485083/2270217
            owner.__save()

        return property(getter, setter)
