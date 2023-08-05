import transaction
from formencode.htmlgen import html
from sqlalchemy.orm.exc import NoResultFound

from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.security import authenticated_userid
from pyramid.security import remember, forget

from goout.security import check_password, encrypt_password
from goout.models import User, Password, DBSession

from base import NotFound, base_data
from base import BaseViewer
from menus import BaseMenu
from forms import LoginForm

##########################
# test new login form
##########################
import deform
import colander

class LoginSchema(colander.Schema):
    username = colander.SchemaNode(
        colander.String(),
        title="User Name",
        )
    password = colander.SchemaNode(
        colander.String(),
        validator=colander.Length(min=5, max=100),
        widget=deform.widget.PasswordWidget(size=20),
        description="Please enter a password.")
    came_from = colander.SchemaNode(
        colander.String(),
        validator=colander.Length(max=500),
        widget=deform.widget.HiddenWidget(),
        default='/',
        )
    
    

    

##########################
# test new login form
##########################

def check_login_form(request):
    username = request.params['username']
    password = request.params['password']
    dbsession = DBSession()
    try:
        user = dbsession.query(User).filter_by(username=username).one()
        request.session['user'] = user
    except NoResultFound:
        return False
    try:
        dbpass = dbsession.query(Password).filter_by(user_id=user.id).one()
    except NoResultFound:
        return False
    return check_password(dbpass.password, password)

class LoginViewer(BaseViewer):
    def __init__(self, request):
        BaseViewer.__init__(self, request)
        self.dbsession = DBSession()
        self.route = self.request.matched_route.name
        # simple dispatch for this viewer
        if self.route == 'logout':
            self.logout_view()
        elif self.route == 'login':
            self.login_view()
        else:
            # we should never hit this error as
            # only "login" and "logout" routes are dispatched
            # to this viewer
            raise RuntimeError, "No such route: %s" % self.route
            
    def __call__(self):
        return self.page_data
        
    def _base_form_view(self):
        #form = LoginForm(self.request.POST)
        #form.add_submit()
        schema = LoginSchema()
        form = deform.Form(schema, buttons=('login',))
        rendered = form.render()
        action = self.request.route_url('login')
        message = "Please Login."
        #rendered = form.render(action, message=message,
        #                       came_from=self.request.url)
        self.page_data['content'] = rendered

    def _login_submitted(self):
        self.dbsession = DBSession()
        came_from = self.request.params['came_from']
        if came_from == self.request.route_url('login'):
            came_from = self.request.route_url('home')
        login = self.request.params['login']
        if check_login_form(self.request):
            headers = remember(self.request, login)
            return HTTPFound(location=came_from,
                             headers=headers)
        else:
            self._base_form_view()
            message = "Login Failed. Try again."
            self.page_data['subheader'] = message

    def login_view(self):
        if 'login' in self.request.params:
            self._login_submitted()
        else:
            self._base_form_view()
            self.page_data['footer'] = str(self.request.params)
            

    def logout_view(self):
        headers = forget(self.request)
        del self.request.session['logged_in']
        location = self.request.route_url('home')
        self._exception = HTTPFound(location=location, headers=headers)
        
    

