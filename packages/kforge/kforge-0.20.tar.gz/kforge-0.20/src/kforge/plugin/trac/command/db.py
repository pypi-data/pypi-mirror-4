from kforge.plugin.trac.command.base import TracEnvironmentCommand
from kforge.ioc import RequiredFeature
from operator import itemgetter

class TracDbCommand(TracEnvironmentCommand):

    envClass = None

    def __init__(self, tracProject=None, env=None):
        super(TracDbCommand, self).__init__(tracProject)
        self.env = env

    @classmethod
    def getEnvClass(self):
        if self.envClass == None:
            from trac.env import Environment
            self.envClass = Environment
        return self.envClass

    @classmethod
    def getResourceNotFoundClass(self):
        if self.resourceNotFoundClass == None:
            from trac.resource import ResourceNotFound
            self.resourceNotFoundClass = ResourceNotFound
        return self.resourceNotFoundClass

    def getEnv(self):
        if not self.env:
            self.env = self.getEnvClass()(self.envPath)
        return self.env

    def resetEnvPath(self, envPath):
        self.envPath = envPath
        self.env = None

    def update(self, query):
        #print "Update: %s" % query
        self.logger.debug('Update: %s' % query)
        env = self.getEnv()
        from trac.db import with_transaction
        @with_transaction(env)
        def execute(db):
            cursor = db.cursor()
            cursor.execute("UPDATE %s;" % query)
            db.commit()

    def insert(self, query):
        #print "Insert: %s" % query
        self.logger.debug('Insert: %s' % query)
        tableName = query.split(' ')[0]
        env = self.getEnv()
        from trac.db import with_transaction
        newId = [None]
        @with_transaction(env)
        def execute(db):
            cursor = db.cursor()
            cursor.execute("INSERT INTO %s;" % query)
            db.commit()
            newId[0] = db.get_last_id(cursor, tableName)
        if newId[0] == None:
            raise Exception, "Couldn't insert record: no ID value was returned (table name: '%s')." % tableName
        return newId[0]

    def select(self, query):
        self.logger.debug('Select: %s' % query)
        env = self.getEnv()
        results = []
        from trac.db import with_transaction
        @with_transaction(env)
        def execute(db):
            cursor = db.cursor()
            cursor.execute("SELECT %s;" % query)
            [results.append(i) for i in cursor]
        return results

