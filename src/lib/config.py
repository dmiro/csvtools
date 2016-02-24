import ConfigParser
import json


class Config(object):

    #
    # public
    #

    @property
    def tools_searches(self):
        return self._tools_searches

    @tools_searches.setter
    def tools_searches(self, value):
        self._tools_searches = value
        self.save()

    @property
    def filterFiles(self):
        return self._filterFiles

    @filterFiles.setter
    def filterFiles(self, value):
        self._filterFiles = value
        self.save()

    @property
    def favFolders(self):
        return self._favFolders

    @favFolders.setter
    def favFolders(self, value):
        self._favFolders = value
        self.save()

    @property
    def matchMode(self):
        return self._matchMode

    @matchMode.setter
    def matchMode(self, value):
        self._matchMode = value
        self.save()

    @property
    def matchCase(self):
        return self._matchCase

    @matchCase.setter
    def matchCase(self, value):
        self._matchCase = value
        self.save()

    @property
    def findAllDocuments(self):
        return self._findAllDocuments

    @findAllDocuments.setter
    def findAllDocuments(self, value):
        self._findAllDocuments = value
        self.save()

    @property
    def showUnmatchedDisabled(self):
        return self._showUnmatchedDisabled

    @showUnmatchedDisabled.setter
    def showUnmatchedDisabled(self, value):
        self._showUnmatchedDisabled = value
        self.save()

    @property
    def showColumnSize(self):
        return self._showColumnSize

    @showColumnSize.setter
    def showColumnSize(self, value):
        self._showColumnSize = value
        self.save()

    @property
    def showColumnDateModified(self):
        return self._showColumnDateModified

    @showColumnDateModified.setter
    def showColumnDateModified(self, value):
        self._showColumnDateModified = value
        self.save()

    # config section: file

    @property
    def file_useCsvWizard(self):
        return self._file_useCsvWizard

    @file_useCsvWizard.setter
    def file_useCsvWizard(self, value):
        self._file_useCsvWizard = value
        self.save()

    @property
    def file_recent(self):
        return self._file_recent

    @file_recent.setter
    def file_recent(self, value):
        self._file_recent = value
        self.save()

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
        self.files = json.loads(self.__get('config', 'files', '[]'))
        self._file_recent = json.loads(self.__get('file', 'recent', '[]'))
        self._tools_searches = json.loads(self.__get('tools', 'searches', '[]'))
        self._filterFiles = json.loads(self.__get('config', 'filterFiles', '[]'))
        self._favFolders = json.loads(self.__get('config', 'favFolders', '[]'))
        self.restore = self.__getBoolean('config', 'restore', True)
        self.headerrow = self.__getBoolean('config', 'headerrow', True)
        self._matchMode = self.__getInt('config', 'matchMode', 0)
        self._matchCase = self.__getBoolean('config', 'matchCase', False)
        self._findAllDocuments = self.__getBoolean('config', 'findAllDocuments', False)
        self._showUnmatchedDisabled = self.__getBoolean('config', 'showUnmatchedDisabled', False)
        self._showColumnSize = self.__getBoolean('config', 'showColumnSize', True)
        self._showColumnDateModified = self.__getBoolean('config', 'showColumnDateModified', True)
        self._file_useCsvWizard = self.__getBoolean('file', 'useCsvWizard', True)

    def save(self):
        self.__set('config', 'files', json.dumps(self.files))
        self.__set('config', 'recent', json.dumps(self._file_recent))
        self.__set('tools', 'searches', json.dumps(self._tools_searches))
        self.__set('config', 'filterFiles', json.dumps(self._filterFiles))
        self.__set('config', 'favFolders', json.dumps(self._favFolders))
        self.__set('config', 'restore', self.restore)
        self.__set('config', 'headerrow', self.headerrow)
        self.__set('config', 'matchMode', self._matchMode)
        self.__set('config', 'matchCase', self._matchCase)
        self.__set('config', 'findAllDocuments', self._findAllDocuments)
        self.__set('config', 'showUnmatchedDisabled', self._showUnmatchedDisabled)
        self.__set('config', 'showColumnSize', self._showColumnSize)
        self.__set('config', 'showColumnDateModified', self._showColumnDateModified)
        self.__set('file', 'useCsvWizard', self._file_useCsvWizard)
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
