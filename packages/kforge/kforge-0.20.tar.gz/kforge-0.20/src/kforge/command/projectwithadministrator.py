from dm.command import Command
import kforge.command

class ProjectWithAdministratorCreate(Command):

    def __init__(self, projectName, personName):
        super(ProjectWithAdministratorCreate, self).__init__(
            projectName=projectName, personName=personName
        )
        self.projectName = projectName
        self.personName = personName

    def execute(self):
        super(ProjectWithAdministratorCreate, self).execute()
        cmdProject = kforge.command.ProjectCreate(
            self.projectName
        )
        cmdProject.execute()
        self.project = cmdProject.project
        cmdMember = kforge.command.MemberCreate(
            self.projectName,
            self.personName,
            roleName='Administrator'
        )
        cmdMember.execute()
 
