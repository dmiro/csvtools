from lib.helpers.iniconfig import IniConfig


class Config(IniConfig):

    # File section
    file_useCsvWizard = IniConfig.iniproperty('file', 'useCsvWizard', True)
    file_recent = IniConfig.iniproperty('file', 'recent', [])
    file_files = IniConfig.iniproperty('file', 'files', [])

    # Recent Files section
    recentfiles_check = IniConfig.iniproperty('recentfiles', 'checkRecentFiles', False)
    recentfiles_maxEntries = IniConfig.iniproperty('recentfiles', 'maxEntries', 20)

    # Tools section
    tools_searches = IniConfig.iniproperty('tools', 'searches', [])
    tools_filterFiles = IniConfig.iniproperty('tools', 'filterFiles', [])
    tools_favFolders = IniConfig.iniproperty('tools', 'favFolders', [])
    tools_matchMode = IniConfig.iniproperty('tools', 'matchMode', 0)
    tools_matchCase = IniConfig.iniproperty('tools', 'matchCase', False)
    tools_findAllDocuments = IniConfig.iniproperty('tools', 'findAllDocuments', False)
    tools_showUnmatchedDisabled = IniConfig.iniproperty('tools', 'showUnmatchedDisabled', False)
    tools_showColumnSize = IniConfig.iniproperty('tools', 'showColumnSize', True)
    tools_showColumnDateModified = IniConfig.iniproperty('tools', 'showColumnDateModified', True)

    # Config section
    config_restore = IniConfig.iniproperty('config', 'restore', True)
    config_headerrow = IniConfig.iniproperty('config', 'headerrow', True)

#
# global
#

config = Config('csvtools.cfg')
