from kforge.plugin.trac.command.base import TracEnvironmentCommand

# Todo: Merge adding missing sessions and setting preferences, so that
# everything is done in a single transaction (currently takes two commits).
#  - select existing sessions
#  - prepare SQL statements
#  - start transaction
#  - insert missing sessions
#  - select+insert/update preferences
#  - commit transaction


class InsertTracSessions(TracEnvironmentCommand):
    """Insert sessions (fails for sessions that already exist)."""

    def __init__(self, tracProject, names):
        super(InsertTracSessions, self).__init__(tracProject)
        self.names = names

    def execute(self):
        sqltmpl = "INSERT INTO session (sid, authenticated, last_visit) VALUES ('%s', 1, '0')"
        inserts = []
        for name in self.names:
            inserts.append(sqltmpl % name)
        try:
            env = self.getEnv()
            from trac.db import with_transaction
            self.lastinsert = ''
            @with_transaction(env)
            def executeSql(db):
                cursor = db.cursor()
                for insert in inserts:
                    self.logger.debug("Executing Trac SQL insert: " + insert)
                    self.lastinsert = insert
                    cursor.execute(insert)
                db.commit()
        except Exception, inst:
            msg = 'Error executing Trac SQL insert statement: %s: %s' % (self.lastinsert, inst)
            self.logger.error(msg)
            raise Exception, msg


class SelectTracSessions(TracEnvironmentCommand):
    """Selects existing sessions."""

    def execute(self):
        env = self.getEnv()
        results = []
        from trac.db import with_transaction
        @with_transaction(env)
        def execute(db):
            cursor = db.cursor()
            cursor.execute("SELECT sid from session;")
            [results.append(i[0]) for i in cursor]
        return results


class AddTracSessions(TracEnvironmentCommand):
    """Adds sessions that do not already exist."""

    def __init__(self, tracProject, names):
        super(AddTracSessions, self).__init__(tracProject)
        self.names = names

    def execute(self):
        names = SelectTracSessions(self.tracProject).execute()
        names = list(set(self.names).difference(set(names)))
        InsertTracSessions(self.tracProject, names).execute()


class SetTracPreferences(TracEnvironmentCommand):
    """Sets preferences from a list of (username, fullname, email) tuples."""

    def __init__(self, tracProject, preferences):
        super(SetTracPreferences, self).__init__(tracProject)
        self.preferences = preferences

    def execute(self):
        # Add sessions so preferences actually show in Trac's preferences tab.
        sessions = [p[0] for p in self.preferences]
        AddTracSessions(self.tracProject, sessions).execute()
        # Having added the sessions, now set the preferences.
        selectTmpl = "SELECT sid from session_attribute WHERE name='%s' AND sid='%s' AND authenticated=1"""
        insertTmpl = "INSERT INTO session_attribute (sid, name, value, authenticated) VALUES ('%s', '%s', '%s', 1)"
        updateTmpl = "UPDATE session_attribute SET value='%s' WHERE sid='%s' AND name='%s' AND authenticated=1"
        statementTriples = []
        for (username, fullname, email) in self.preferences:
            #fullname = fullname.encode('utf8')
            fullname = fullname.replace("'", "''")
            email = email.replace("'", "''")
            select = selectTmpl % ('name', username)
            insert = insertTmpl % (username, 'name', fullname)
            update = updateTmpl % (fullname, username, 'name')
            statementTriples.append((select, insert, update))
            select = selectTmpl % ('email', username)
            insert = insertTmpl % (username, 'email', email)
            update = updateTmpl % (email, username, 'email')
            statementTriples.append((select, insert, update))
        try:
            env = self.getEnv()
            from trac.db import with_transaction
            self.laststatement = ''
            @with_transaction(env)
            def executeSql(db):
                cursor = db.cursor()
                for select, insert, update in statementTriples:
                    self.logger.debug("Executing Trac SQL select: " + select)
                    self.laststatement = select
                    cursor.execute(select)
                    if not [i for i in cursor]:
                        self.logger.debug("Executing Trac SQL insert: " + insert)
                        self.laststatement = insert
                        cursor.execute(insert)
                    else:
                        self.logger.debug("Executing Trac SQL update: " + update)
                        self.laststatement = update
                        cursor.execute(update)
                db.commit()
        except Exception, inst:
            msg = 'Error executing Trac SQL statement: %s: %s' % (self.laststatement.encode('utf8'), inst)
            self.logger.error(msg)
            raise Exception, msg


class GetTracPreferences(TracEnvironmentCommand):

    def __init__(self, tracProject, username):
        super(GetTracPreferences, self).__init__(tracProject)
        self.username = username

    def execute(self):
        selectTmpl = "SELECT value from session_attribute WHERE name='%s' "
        selectTmpl += "AND sid='%s' AND authenticated=1"
        selectFullname = selectTmpl % ('name', self.username)
        selectEmail = selectTmpl % ('email', self.username)
        env = self.getEnv()
        emailResults = []
        fullnameResults = []
        from trac.db import with_transaction
        @with_transaction(env)
        def executeSql(db):
            cursor = db.cursor()
            cursor.execute(selectFullname)
            [fullnameResults.append(i[0]) for i in cursor]
            cursor.execute(selectEmail)
            [emailResults.append(i[0]) for i in cursor]
        fullname = fullnameResults and fullnameResults[0] or None
        email = emailResults and emailResults[0] or None
        return self.username, fullname, email

