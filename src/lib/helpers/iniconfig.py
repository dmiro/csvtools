import ConfigParser
import json


class IniConfig(object):

    #
    # class methods
    #

    @classmethod
    def booleanProperty(cls, section, option, default):
        def getter(self):
            return self.__get(section, option, default,
                              self.__config.get)
        def setter(self, value):
            self.__set(section, option, value)
        return property(getter, setter)

    @classmethod
    def intProperty(cls, section, option, default):
        def getter(self):
            return self.__get(section, option, default,
                              self.__config.getint)
        def setter(self, value):
            self.__set(section, option, value)
        return property(getter, setter)

    @classmethod
    def jsonProperty(cls, section, option, default):
        def getter(self):
            return json.loads(self.__get(section, option, default,
                                         self.__config.get))
        def setter(self, value):
            self.__set(section, option, json.dumps(value))
        return property(getter, setter)

    #
    # private
    #

    def __getProperty(self, section, option):
        attrNameMangled = '_' + self.__class__.__name__ + '__' + section + '_' + option
        if hasattr(self, attrNameMangled):
            return getattr(self, attrNameMangled)
        return None

    def __setProperty(self, section, option, value):
        attrNameMangled = '_' + self.__class__.__name__ + '__' + section + '_' + option
        setattr(self, attrNameMangled, value)

    def __get(self, section, option, default, configGetter):
        value = self.__getProperty(section, option)
        if not value:
            if not self.__config.has_section(section):
                self.__config.add_section(section)
            if self.__config.has_option(section, option):
                value = configGetter(section, option)
            else:
                value = default
            self.__setProperty(section, option, value)
        return value

    def __set(self, section, option, value):
        self.__setProperty(section, option, value)
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
        self.__load()
