import ConfigParser
import json


class IniConfig(object):

    #
    # class methods
    #

    @classmethod
    def booleanProperty(cls, section, option, default):
        def getter(self):
            return self.__getBoolean(section, option, default)
        def setter(self, value):
            self.__set(section, option, value)
            #self.__save()
        return property(getter, setter)

    @classmethod
    def intProperty(cls, section, option, default):
        def getter(self):
            return self.__getInt(section, option, default)
        def setter(self, value):
            self.__set(section, option, value)
            #self.__save()
        return property(getter, setter)

    @classmethod
    def jsonProperty(cls, section, option, default):
        def getter(self):
            return json.loads(self.__get(section, option, default))
        def setter(self, value):
            self.__set(section, option, json.dumps(value))
            #self.__save()
        return property(getter, setter)

    #
    # private
    #

    def __getBoolean(self, section, option, default):
        self.__load()
        if not self.__config.has_section(section):
            self.__config.add_section(section)
        if self.__config.has_option(section, option):
            return self.__config.getboolean(section, option)
        else:
            return default

    def __getInt(self, section, option, default):
        self.__load()
        if not self.__config.has_section(section):
            self.__config.add_section(section)
        if self.__config.has_option(section, option):
            return self.__config.getint(section, option)
        else:
            return default

    def __get(self, section, option, default):
        self.__load()
        if not self.__config.has_section(section):
            self.__config.add_section(section)
        if self.__config.has_option(section, option):
            return self.__config.get(section, option)
        else:
            return default

    def __set(self, section, option, value):
        if not self.__config.has_section(section):
            self.__config.add_section(section)
        self.__config.set(section, option, value)
        self.__save()

    def __load(self):
        self.__config.read(self.filename)

    def __save(self):
        with open(self.filename, 'wb') as configfile:
            self.__config.write(configfile)

    #
    # init
    #

    def __init__(self, filename):
        super(IniConfig, self).__init__()
        self.filename = filename
        self.__config = ConfigParser.ConfigParser()
        #self.__load()
