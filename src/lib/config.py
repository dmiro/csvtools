import ConfigParser
import json

class Config(object):

    #
    # public
    #

    @property
    def searches(self):
        return self._searches

    @searches.setter
    def searches(self, value):
        self._searches = value
        self.save()

    @property
    def recent(self):
        return self._recent

    @recent.setter
    def recent(self, value):
        self._recent = value
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

    #
    # private
    #

    def __getBoolean(self, config, section, option, default):
        if not config.has_section(section):
            config.add_section(section)
        if config.has_option(section, option):
            return config.getboolean(section, option)
        else:
            return default

    def __getInt(self, config, section, option, default):
        if not config.has_section(section):
            config.add_section(section)
        if config.has_option(section, option):
            return config.getint(section, option)
        else:
            return default

    def __get(self, config, section, option, default):
        if not config.has_section(section):
            config.add_section(section)
        if config.has_option(section, option):
            return config.get(section, option)
        else:
            return default

    def __load(self):
        config = ConfigParser.ConfigParser()
        config.read('csvtools.cfg')
        self.files = json.loads(self.__get(config, 'config', 'files', '[]'))
        self._recent = json.loads(self.__get(config, 'config', 'recent', '[]'))
        self._searches = json.loads(self.__get(config, 'config', 'searches', '[]'))
        self._filterFiles = json.loads(self.__get(config, 'config', 'filterFiles', '[]'))
        self._favFolders = json.loads(self.__get(config, 'config', 'favFolders', '[]'))
        self.restore = self.__getBoolean(config, 'config', 'restore', True)
        self.headerrow = self.__getBoolean(config, 'config', 'headerrow', True)
        self._matchMode = self.__getInt(config, 'config', 'matchMode', 0)
        self._matchCase = self.__getBoolean(config, 'config', 'matchCase', False)
        self._findAllDocuments = self.__getBoolean(config, 'config', 'findAllDocuments', False)
        self._showUnmatchedDisabled = self.__getBoolean(config, 'config', 'showUnmatchedDisabled', False)
        self._showColumnSize = self.__getBoolean(config, 'config', 'showColumnSize', True)
        self._showColumnDateModified = self.__getBoolean(config, 'config', 'showColumnDateModified', True)
        self._file_useCsvWizard = self.__getBoolean(config, 'file', 'useCsvWizard', True)

    def save(self):
        config = ConfigParser.ConfigParser()
        if not config.has_section('config'):
            config.add_section('config')
        if not config.has_section('file'):
            config.add_section('file')
        config.set('config', 'files', json.dumps(self.files))
        config.set('config', 'recent', json.dumps(self._recent))
        config.set('config', 'searches', json.dumps(self._searches))
        config.set('config', 'filterFiles', json.dumps(self._filterFiles))
        config.set('config', 'favFolders', json.dumps(self._favFolders))
        config.set('config', 'restore', self.restore)
        config.set('config', 'headerrow', self.headerrow)
        config.set('config', 'matchMode', self._matchMode)
        config.set('config', 'matchCase', self._matchCase)
        config.set('config', 'findAllDocuments', self._findAllDocuments)
        config.set('config', 'showUnmatchedDisabled', self._showUnmatchedDisabled)
        config.set('config', 'showColumnSize', self._showColumnSize)
        config.set('config', 'showColumnDateModified', self._showColumnDateModified)
        config.set('file', 'useCsvWizard', self._file_useCsvWizard)
        with open('csvtools.cfg', 'wb') as configfile:
            config.write(configfile)

    #
    # init
    #

    def __init__(self, *args):
        object.__init__(self, *args)
        self.__load()


#
# global
#

config = Config()
