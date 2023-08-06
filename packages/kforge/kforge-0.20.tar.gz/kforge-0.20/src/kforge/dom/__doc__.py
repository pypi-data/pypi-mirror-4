"""
This module documents kforge.dom which provides a registry 
for entities in the KForge Domain Model.

The registry supports commands in the service layer, and 
calls upon a persistence layer for domain object persistence.

It follows 'Domain Model (116)' [Fowler, 2003].

The following listing describes the architecture of the registry:
(See usage examples (below) for more information.)
    
    registry:
        licenses[id]: License
            name
        sessions[key]: Session
            key
            startTime
        people[name]: Person
            name
            fullname
            memberships[project]: Member
                person
                project
                role
            sessions[key]: Session
        projects[name]: Project
            name
            title
            description
            purpose
            services[plugin]: Service
                name
                plugin
            members[person]: Member
                person
                project
                role
            licenses[id]: ProjecLicense
                license
        plugins[name]: Plugin
            name
            services[plugin]: Service
                name
                plugin
            Permissions[action]: Permission
                action
                plugin (not protection object - todo: update documentation)
        actions[name]: Action
            name
        roles[name]: Role
            name
            grants[permission]: Grant
                permission
                role
            
    NB: Each item in an indented list is an attribute of the item above.
    Items with []'s are registers. Registers emulate the dict type and 
    support such expressions as: for i in a, len(a), a.keys(), a[key], etc.
    The name inside the []'s is the attribute of the entity used to index 
    the entities in the register. The name after the colon is the type 
    of entity recorded in the register.
    

Example usage of the KForge domain model:

    # Initialise KForge registry.
    
    import kforge.dom
    registry = kforge.dom.DomainRegistry()
    
    
    # Register KForge entities.
    
    beans = registry.projects.create('beans')
    jane = registry.people.create('jane')
    
    example = registry.plugins.create('example')
    
    service = beans.services.create(example)
    member = beans.members.create(jane)


    # Read registered entities.

    # various ways of listing each registered person
    
    for name in registry.people.keys():
        person = registry.people[name]
        print person.name, person.fullname
        
    for person in registry.people:
        print person.name, person.fullname
        
    [(person.name, person.fullname) for person in registry.people]
    
    registry.people.keys()  # names only this time
    
    # list names of all registered members of a named project
    projectName = 'beans'
    beans = registry.projects[projectName]
    beans = registry.projects.get(projectName)
    print [member.person.name for member in beans.members]
    
    # count registered projects
    totalRegisteredProjects = registry.projects.count()
    totalRegisteredProjects = len(registry.projects)

    # list all registered projects on the system
    print [project.name for project in registry.projects]
    print registry.projects.keys()

    # list all project services for given plugin
    project.services.findDomainObjects(plugin=plugin)
    
    # list all plugin services for given project
    plugin.services.findDomainObjects(project=project)

    # count members of project
    totalMembers = beans.members.count()
    totalMembers = len(beans.members)
   
   
    # Update registered entities.

    # retitle Project
    if 'beans' in registry.projects:
        beans = registry.projects['beans']
        project.title = 'The Beans'
        project.save()

    # rename Person
    if 'joe' in registry.people:
        person = registry.people['joe']
        person.fullname = 'Joe Tickle'
        person.save()


    # Delete registered entities.
    
    projectName = 'beans'
    personName = 'jack'
    
    # cautiously remove person from project
    if projectName in registry.projects:
        project = registry.projects[projectName]
        
        if personName in project.members:
            person = registry.people[personName]
            
            if person project.members:
                del project.members[person]

    # incautiously remove person and project
    del people['joe']
    del projects['beans']
"""
