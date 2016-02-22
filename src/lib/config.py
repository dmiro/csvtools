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

    #
    # private
    #

    def _load(self):
        config = ConfigParser.ConfigParser({'files': '[]',
                                            'recent': '[]',
                                            'searches':'[]',
                                            'filterFiles':'[]',
                                            'favFolders':'[]',
                                            'restore':'True',
                                            'headerrow':'True',
                                            'matchMode': '0',
                                            'matchCase': 'False',
                                            'findAllDocuments': 'False',
                                            'showUnmatchedDisabled': 'False',
                                            'showColumnSize': 'True',
                                            'showColumnDateModified': 'True'})
        config.read('csvtools.cfg')
        if not config.has_section('config'):
            config.add_section('config')
        self.files = json.loads(config.get('config', 'files'))
        self._recent = json.loads(config.get('config', 'recent'))
        self._searches = json.loads(config.get('config', 'searches'))
        self._filterFiles = json.loads(config.get('config', 'filterFiles'))
        self._favFolders = json.loads(config.get('config', 'favFolders'))
        self.restore = config.getboolean('config', 'restore')
        self.headerrow = config.getboolean('config', 'headerrow')
        self._matchMode = config.getint('config', 'matchMode')
        self._matchCase = config.getboolean('config', 'matchCase')
        self._findAllDocuments = config.getboolean('config', 'findAllDocuments')
        self._showUnmatchedDisabled = config.getboolean('config', 'showUnmatchedDisabled')
        self._showColumnSize = config.getboolean('config', 'showColumnSize')
        self._showColumnDateModified = config.getboolean('config', 'showColumnDateModified')

    def save(self):
        config = ConfigParser.ConfigParser()
        if not config.has_section('config'):
            config.add_section('config')
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
        with open('csvtools.cfg', 'wb') as configfile:
            config.write(configfile)

    #
    # init
    #
    
    def __init__(self, *args):
        object.__init__(self, *args)
        self._load()



config = Config()
