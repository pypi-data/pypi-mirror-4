from dm.regexps import *
sshKeyString = 'ssh\-(rsa|dss) \S+ \S+'
projectName = '[0-9a-zA-Z\_\-]+'
reservedProjectName = 'home|feed|create|find|search|update|delete|purge|admin|person|project|login|logout|recover|media|about|mailman'
pluginName = '[0-9a-z\_\-]+'
reservedPluginName = 'home|create|find|search|update|delete|purge'
serviceName = '[0-9a-zA-Z\_\-]+'
