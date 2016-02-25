import ConfigParser
import json


class Config(object):

    #
    # class method
    #

    def configProperty(propName):
        def getter(self):
            propNameMangled = '_' + self.__class__.__name__ + '__' + propName
            return getattr(self, propNameMangled)
        def setter(self, value):
            propNameMangled = '_' + self.__class__.__name__ + '__' + propName
            setattr(self, propNameMangled, value)
            self.__save()
        return property(getter, setter)

    #
    # public
    #

    # file section

    file_useCsvWizard = configProperty('file_useCsvWizard')
    file_recent = configProperty('file_recent')
    file_files = configProperty('file_files')

    # tools section

    tools_searches = configProperty('tools_searches')
    tools_filterFiles = configProperty('tools_filterFiles')
    tools_favFolders = configProperty('tools_favFolders')
    tools_matchMode = configProperty('tools_matchMode')
    tools_matchCase = configProperty('tools_matchCase')
    tools_findAllDocuments = configProperty('tools_findAllDocuments')
    tools_showUnmatchedDisabled = configProperty('tools_showUnmatchedDisabled')
    tools_showColumnSize = configProperty('tools_showColumnSize')
    tools_showColumnDateModified = configProperty('tools_showColumnDateModified')

    # config section

    config_restore = configProperty('config_restore')
    config_headerrow = configProperty('config_headerrow')

    #
    # private
    #

    def __getBoolean(self, section, option, default):
        if not self.__config.has_section(section):
            self.__config.add_section(section)
        if self.__config.has_option(section, option):
            return self.__config.getboolean(section, option)
        else:
            return default

    def __getInt(self, section, option, default):
        if not self.__config.has_section(section):
            self.__config.add_section(section)
        if self.__config.has_option(section, option):
            return self.__config.getint(section, option)
        else:
            return default

    def __get(self, section, option, default):
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

    def __load(self):
        self.__config.read('csvtools.cfg')
        # tools section
        self.__tools_searches = json.loads(self.__get('tools', 'searches', '[]'))
        self.__tools_filterFiles = json.loads(self.__get('tools', 'filterFiles', '[]'))
        self.__tools_favFolders = json.loads(self.__get('tools', 'favFolders', '[]'))
        self.__tools_matchMode = self.__getInt('tools', 'matchMode', 0)
        self.__tools_matchCase = self.__getBoolean('tools', 'matchCase', False)
        self.__tools_findAllDocuments = self.__getBoolean('tools', 'findAllDocuments', False)
        self.__tools_showUnmatchedDisabled = self.__getBoolean('tools', 'showUnmatchedDisabled', False)
        self.__tools_showColumnSize = self.__getBoolean('tools', 'showColumnSize', True)
        self.__tools_showColumnDateModified = self.__getBoolean('tools', 'showColumnDateModified', True)
        # file section
        self.__file_recent = json.loads(self.__get('file', 'recent', '[]'))
        self.__file_useCsvWizard = self.__getBoolean('file', 'useCsvWizard', True)
        self.__file_files = json.loads(self.__get('file', 'files', '[]'))
        # config section
        self.__config_restore = self.__getBoolean('config', 'restore', True)
        self.__config_headerrow = self.__getBoolean('config', 'headerrow', True)

    def __save(self):
        # tools section
        self.__set('tools', 'searches', json.dumps(self.__tools_searches))
        self.__set('tools', 'filterFiles', json.dumps(self.__tools_filterFiles))
        self.__set('tools', 'favFolders', json.dumps(self.__tools_favFolders))
        self.__set('tools', 'matchMode', self.__tools_matchMode)
        self.__set('tools', 'matchCase', self.__tools_matchCase)
        self.__set('tools', 'findAllDocuments', self.__tools_findAllDocuments)
        self.__set('tools', 'showUnmatchedDisabled', self.__tools_showUnmatchedDisabled)
        self.__set('tools', 'showColumnSize', self.__tools_showColumnSize)
        self.__set('tools', 'showColumnDateModified', self.__tools_showColumnDateModified)
        # file section
        self.__set('file', 'recent', json.dumps(self.__file_recent))
        self.__set('file', 'useCsvWizard', self.__file_useCsvWizard)
        self.__set('file', 'files', json.dumps(self.__file_files))
        # config section
        self.__set('config', 'restore', self.__config_restore)
        self.__set('config', 'headerrow', self.__config_headerrow)

        with open('csvtools.cfg', 'wb') as configfile:
            self.__config.write(configfile)

    #
    # init
    #

    def __init__(self, *args):
        object.__init__(self, *args)
        self.__config = ConfigParser.ConfigParser()
        self.__load()


#
# global
#

config = Config()
