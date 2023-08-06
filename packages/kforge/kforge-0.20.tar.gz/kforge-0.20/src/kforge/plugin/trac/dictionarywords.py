from kforge.dictionarywords import *
from kforge.plugin.base import dictionary, setWord
import os

TRAC_ADMIN_SCRIPT = ExecutableFileSetting('trac.admin_script', umask=0o22)
# Todo: Rename _path to _dir.
TRAC_HTDOCS_PATH = 'trac.htdocs_path'
TRAC_WSGI_SCRIPT_PATH = WsgiScriptSetting('trac.wsgi_file')
TRAC_WSGI_PROCESS_GROUP = 'trac.wsgi_process_group'
TRAC_ADMIN_PERMS = 'trac.admin_permissions'
TRAC_VIEW_PERMS = 'trac.view_permissions'
TRAC_WRITE_PERMS = 'trac.write_permissions'
TRAC_SET_PREFS_FOR_ALL_PEOPLE = 'trac.set_preferences_for_all_people'

defaultAdminScriptPath = os.path.join(dictionary[VIRTUALENVBIN_PATH], 'trac-admin')
defaultWsgiScriptPath = os.path.join(dictionary[FILESYSTEM_PATH], 'wsgi', 'trac.wsgi')
defaultAdminPerms = 'TRAC_ADMIN'
defaultViewPerms = 'BROWSER_VIEW, CHANGESET_VIEW, FILE_VIEW, \
LOG_VIEW, MILESTONE_VIEW, REPORT_SQL_VIEW, REPORT_VIEW, \
ROADMAP_VIEW, SEARCH_VIEW, TICKET_VIEW, TIMELINE_VIEW, WIKI_VIEW'
defaultWritePerms = 'TICKET_CREATE, TICKET_MODIFY, \
WIKI_CREATE, WIKI_MODIFY'
defaultWsgiProcessGroup = dictionary[WSGI_PROCESS_GROUP]

setWord(TRAC_ADMIN_SCRIPT, defaultAdminScriptPath)
setWord(TRAC_HTDOCS_PATH, '')
setWord(TRAC_WSGI_SCRIPT_PATH, defaultWsgiScriptPath)
setWord(TRAC_WSGI_PROCESS_GROUP, defaultWsgiProcessGroup)
setWord(TRAC_ADMIN_PERMS, defaultAdminPerms)
setWord(TRAC_VIEW_PERMS, defaultViewPerms)
setWord(TRAC_WRITE_PERMS, defaultWritePerms)
setWord(TRAC_SET_PREFS_FOR_ALL_PEOPLE, '')

