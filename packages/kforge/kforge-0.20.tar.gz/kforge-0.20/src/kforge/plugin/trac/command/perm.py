from kforge.plugin.trac.command.base import TracEnvironmentCommand
from kforge.plugin.trac.exceptions import TracPermissionSpecError 
import re

class SetTracPermissions(TracEnvironmentCommand):

    permissionSystemClass = None

    def __init__(self, tracProject, specs=[]):
        super(SetTracPermissions, self).__init__(tracProject)
        self.permissionSystem = None
        self.specs = specs
        self.actions = None

    @classmethod
    def getPermissionSystemClass(self):
        if self.permissionSystemClass == None:
            from trac.perm import PermissionSystem
            self.permissionSystemClass = PermissionSystem
        return self.permissionSystemClass

    def getPermissionSystem(self):
        if self.permissionSystem == None:
            p = self.getPermissionSystemClass()(self.getEnv())
            self.permissionSystem = p
        return self.permissionSystem

    def listActions(self):
        if self.actions == None:
            self.actions = self.getPermissionSystem().get_actions()
        return self.actions

    def grant(self, username, action):
        if action not in self.listActions():
            raise TracPermissionSpecError, "Action not supported: %s" % action
        self.getPermissionSystem().grant_permission(username, action)

    def revoke(self, username, action):
        if action not in self.listActions():
            raise TracPermissionSpecError, "Action not supported: %s" % action
        self.getPermissionSystem().revoke_permission(username, action)

    def listGrants(self, username):
        return self.getPermissionSystem().get_user_permissions(username)

    def exists(self, username, action):
        if action not in self.listActions():
            raise TracPermissionSpecError, "Action not supported: %s" % action
        return action in self.listGrants(username)

    def execute(self):
        for spec in self.specs:
            parts = spec.split(' ')
            if len(parts) != 3:
                msg = "Permission command spec needs 3 parts (METHOD USERNAME ACTION) but there were %s: '%s'" % (len(parts), spec)
                raise TracPermissionSpecError, msg
            method = parts[0]
            username = parts[1]
            action = parts[2]
            if method == 'grant':
                self.grant(username, action)
            elif method == 'revoke':
                action = parts[2]
                if action == '*':
                    for action in self.listGrants(username):
                        self.revoke(username, action)
                else:
                    self.revoke(username, action)
            elif method == 'assert':
                if not self.exists(username, action):
                    msg = "User '%s' not granted action '%s'." % (username, action)
                    raise Exception, msg
            elif method == 'assertnot':
                if self.exists(username, action):
                    msg = "User '%s' is granted action '%s'." % (username, action)
                    raise Exception, msg
            else:
                raise TracPermissionSpecError, "Method not supported: %s" % method

