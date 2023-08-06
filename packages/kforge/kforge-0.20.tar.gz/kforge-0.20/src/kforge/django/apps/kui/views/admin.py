from kforge.django.apps.kui.views.base import KforgeView
import dm.view.admin

class AdminView(KforgeView):

    def getMajorNavigationItem(self):
        return '/admin/model/'

class AdminIndexView(AdminView, dm.view.admin.AdminIndexView):
    pass

class AdminModelView(AdminView, dm.view.admin.AdminModelView):
    pass

class AdminListView(AdminView, dm.view.admin.AdminListView):
    pass 

class AdminCreateView(AdminView, dm.view.admin.AdminCreateView):
    pass

class AdminReadView(AdminView, dm.view.admin.AdminReadView):
    pass

class AdminUpdateView(AdminView, dm.view.admin.AdminUpdateView):
    pass

class AdminDeleteView(AdminView, dm.view.admin.AdminDeleteView):
    pass

class AdminListHasManyView(AdminView, dm.view.admin.AdminListHasManyView):
    pass

class AdminCreateHasManyView(AdminView, dm.view.admin.AdminCreateHasManyView):
    pass

class AdminReadHasManyView(AdminView, dm.view.admin.AdminReadHasManyView):
    pass

class AdminUpdateHasManyView(AdminView, dm.view.admin.AdminUpdateHasManyView):
    pass

class AdminDeleteHasManyView(AdminView, dm.view.admin.AdminDeleteHasManyView):
    pass


def index(request):
    view = AdminIndexView(request=request)
    return view.getResponse()

def model(request):
    view = AdminModelView(request=request)
    return view.getResponse()

def list(request, className):
    view = AdminListView(
        request=request,
        domainClassName=className,
    )
    return view.getResponse()

def create(request, className):
    view = AdminCreateView(
        request=request,
        domainClassName=className,
    )
    return view.getResponse()

def read(request, className, objectKey):
    view = AdminReadView(
        request=request,
        domainClassName=className,
        domainObjectKey=objectKey,
    )
    return view.getResponse()

def update(request, className, objectKey):
    view = AdminUpdateView(
        request=request,
        domainClassName=className,
        domainObjectKey=objectKey,
    )
    return view.getResponse()

def delete(request, className, objectKey):
    view = AdminDeleteView(
        request=request,
        domainClassName=className,
        domainObjectKey=objectKey,
    )
    return view.getResponse()

def listHasMany(request, className, objectKey, hasMany):
    view = AdminListHasManyView(
        request=request,
        domainClassName=className,
        domainObjectKey=objectKey,
        hasManyName=hasMany,
    )
    return view.getResponse()

def createHasMany(request, className, objectKey, hasMany):
    view = AdminCreateHasManyView(
        request=request,
        domainClassName=className,
        domainObjectKey=objectKey,
        hasManyName=hasMany,
    )
    return view.getResponse()

def readHasMany(request, className, objectKey, hasMany, attrKey):
    view = AdminReadHasManyView(
        request=request,
        domainClassName=className,
        domainObjectKey=objectKey,
        hasManyName=hasMany,
        hasManyKey=attrKey,
    )
    return view.getResponse()

def updateHasMany(request, className, objectKey, hasMany, attrKey):
    view = AdminUpdateHasManyView(
        request=request,
        domainClassName=className,
        domainObjectKey=objectKey,
        hasManyName=hasMany,
        hasManyKey=attrKey,
    )
    return view.getResponse()

def deleteHasMany(request, className, objectKey, hasMany, attrKey):
    view = AdminDeleteHasManyView(
        request=request,
        domainClassName=className,
        domainObjectKey=objectKey,
        hasManyName=hasMany,
        hasManyKey=attrKey,
    )
    return view.getResponse()


viewDict = {}
viewDict['ListView']   = AdminListView
viewDict['CreateView'] = AdminCreateView
viewDict['ReadView']   = AdminReadView
viewDict['UpdateView'] = AdminUpdateView
viewDict['DeleteView'] = AdminDeleteView

def view(request, caseName, actionName, className, objectKey):
    if caseName == 'model':
        viewClassName = actionName.capitalize() + 'View'
        viewClass = viewDict[viewClassName]
        viewArgs = []
        if className:
            viewArgs.append(className)
            if objectKey:
                viewArgs.append(objectKey)
        view = viewClass(request=request)
        return view.getResponse(*viewArgs)
    raise "Case '%s' not supported." % caseName

