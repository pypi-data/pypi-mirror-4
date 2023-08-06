import os
import commands

import dm.util.db

import kforge.ioc

class Database(dm.util.db.Database):
    
    features = kforge.ioc.features

    def _getSystemDictionary(self):
        import kforge.dictionary
        systemDictionary = kforge.dictionary.SystemDictionary()
        return systemDictionary
            
    def init(self):
        """
        Initialises service database by creating initial domain object records.
        """
        import kforge.soleInstance
        commandSet = kforge.soleInstance.application.commands
        domainModelCommandName = 'InitialiseDomainModel'
        domainModelCommandClass = commandSet[domainModelCommandName]
        domainModelCommand = domainModelCommandClass()
        domainModelCommand.execute()

