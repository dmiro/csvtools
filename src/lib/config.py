from lib.helpers.iniconfig import *


class Config(IniConfig):

    # file section
    file_useCsvWizard = IniConfig.booleanProperty('file', 'useCsvWizard', True)
    file_recent = IniConfig.jsonProperty('file', 'recent', '[]')
    file_files = IniConfig.jsonProperty('file', 'files', '[]')

    # tools section
    tools_searches = IniConfig.jsonProperty('tools', 'searches', '[]')
    tools_filterFiles = IniConfig.jsonProperty('tools', 'filterFiles', '[]')
    tools_favFolders = IniConfig.jsonProperty('tools', 'favFolders', '[]')
    tools_matchMode = IniConfig.intProperty('tools', 'matchMode', 0)
    tools_matchCase = IniConfig.booleanProperty('tools', 'matchCase', False)
    tools_findAllDocuments = IniConfig.booleanProperty('tools', 'findAllDocuments', False)
    tools_showUnmatchedDisabled = IniConfig.booleanProperty('tools', 'showUnmatchedDisabled', False)
    tools_showColumnSize = IniConfig.booleanProperty('tools', 'showColumnSize', True)
    tools_showColumnDateModified = IniConfig.booleanProperty('tools', 'showColumnDateModified', True)

    # config section
    config_restore = IniConfig.booleanProperty('config', 'restore', True)
    config_headerrow = IniConfig.booleanProperty('config', 'headerrow', True)

    #
    # init
    #

    def __init__(self, *args):
        super(Config, self).__init__(*args)

#
# global
#

config = Config('csvtools.cfg')
