import ConfigParser
import json


class Config(object):

    #
    # public
    #

    # file section

    @property
    def file_useCsvWizard(self):
        return self.__file_useCsvWizard

    @file_useCsvWizard.setter
    def file_useCsvWizard(self, value):
        self.__file_useCsvWizard = value
        self.__save()

    @property
    def file_recent(self):
        return self.__file_recent

    @file_recent.setter
    def file_recent(self, value):
        self.__file_recent = value
        self.__save()

    @property
    def file_files(self):
        return self.__file_files

    @file_files.setter
    def file_files(self, value):
        self.__file_files = value
        self.__save()

    # tools section
    
    @property
    def tools_searches(self):
        return self.__tools_searches

    @tools_searches.setter
    def tools_searches(self, value):
        self.__tools_searches = value
        self.__save()

    @property
    def tools_filterFiles(self):
        return self.__tools_filterFiles

    @tools_filterFiles.setter
    def tools_filterFiles(self, value):
        self.__tools_filterFiles = value
        self.__save()

    @property
    def tools_favFolders(self):
        return self.__tools_favFolders

    @tools_favFolders.setter
    def tools_favFolders(self, value):
        self.__tools_favFolders = value
        self.__save()

    @property
    def tools_matchMode(self):
        return self.__tools_matchMode

    @tools_matchMode.setter
    def tools_matchMode(self, value):
        self.__tools_matchMode = value
        self.__save()

    @property
    def tools_matchCase(self):
        return self.__tools_matchCase

    @tools_matchCase.setter
    def tools_matchCase(self, value):
        self.__tools_matchCase = value
        self.__save()

    @property
    def tools_findAllDocuments(self):
        return self.__tools_findAllDocuments

    @tools_findAllDocuments.setter
    def tools_findAllDocuments(self, value):
        self.__tools_findAllDocuments = value
        self.__save()

    @property
    def tools_showUnmatchedDisabled(self):
        return self.__tools_showUnmatchedDisabled

    @tools_showUnmatchedDisabled.setter
    def tools_showUnmatchedDisabled(self, value):
        self.__tools_showUnmatchedDisabled = value
        self.__save()

    @property
    def tools_showColumnSize(self):
        return self.__tools_showColumnSize

    @tools_showColumnSize.setter
    def tools_showColumnSize(self, value):
        self.__tools_showColumnSize = value
        self.__save()

    @property
    def tools_showColumnDateModified(self):
        return self.__tools_showColumnDateModified

    @tools_showColumnDateModified.setter
    def tools_showColumnDateModified(self, value):
        self.__tools_showColumnDateModified = value
        self.__save()

    # config section

    @property
    def config_restore(self):
        return self.__config_restore

    @config_restore.setter
    def config_restore(self, value):
        self.__config_restore = value
        self.__save()

    @property
    def config_headerrow(self):
        return self.__config_headerrow

    @config_headerrow.setter
    def config_headerrow(self, value):
        self.__config_headerrow = value
        self.__save()

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
