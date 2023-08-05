from pyramid.security import Allow, Everyone, Authenticated

class RootFactory(object):
    __acl__ = [
        (Allow, Authenticated, 'view'),
        (Allow, 'role:admin', 'admin'),
        (Allow, 'role:host', 'host_venue'),
        (Allow, 'role:host', 'host_event')
        ]
    def __init__(self, request):
        pass
    

# the acl entries are allow/deny, group, permission
class RootGroupFactory(object):
    __name__ = ""
    __acl__ = [
        (Allow, Everyone, 'public'),
        (Allow, Authenticated, 'user'),
        (Allow, 'manager', 'manage'),
        (Allow, 'admin', ('admin', 'manage')),
        (Allow, 'manager', ('wiki_add', 'wiki_edit')),
        (Allow, 'admin', ('wiki_add', 'wiki_edit')),
        ]
    def __init__(self, request):
        pass
    
    
