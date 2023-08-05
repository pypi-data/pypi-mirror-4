from datetime import datetime

import transaction
from formencode.htmlgen import html
from mako.template import Template
from sqlalchemy.orm.exc import NoResultFound

from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.security import authenticated_userid

from menus import BaseMenu, TopBar


from trumpet.models.base import DBSession
from trumpet.models.usergroup import User



JAVASCRIPT_TEMPLATE = """
<script type="text/javascript" language="javascript">
    // <![CDATA[
      ${codeblock}
    // ]]>
</script>
"""
JavaScriptTemplate = Template(JAVASCRIPT_TEMPLATE)

QJAVASCRIPT_TEMPLATE = '<script type="text/javascript">${code}</script>'
QJavaScriptTemplate = Template(QJAVASCRIPT_TEMPLATE)




def submit_button(value):
    return '<input type="submit" value="%s" />' % value

def error_menu(request):
    menu = BaseMenu(header='Error Menu', class_='errormenu')
    menu.append(html.tr(html.td(html.p('Explanation:  ${explanation}'))))
    menu.append(html.tr(html.td(html.p('Detail:  ${detail}'))))
    menu.append_new_entry('back', request.referrer)
    menu.append_new_entry('home', '/')
    return menu

def NotFound(request, detail):
            menu = error_menu(request)
            return HTTPNotFound(detail=detail,
                                body_template=unicode(menu))

            
            
def make_top_bar(request):
    bar = TopBar(request.matched_route.name)
    bar.entries['Home'] = '/'
    if 'user' in request.session:
        user = request.session['user']
        if user.role == 'admin':
            url = request.route_url('admin', context='main')
            bar.entries['admin'] = url
        elif user.role == 'host':
            url = request.route_url('host', context='main')
            bar.entries['Event Administration'] = url
    bar.entries['Reload'] = 'javascript:document.location.reload()'
    return bar

def base_data(request):
    if 'logged_in' in request.session and request.session['logged_in']:
        logged_in = request.session.get('logged_in')
    else:
        logged_in = authenticated_userid(request)
        if logged_in:
            request.session['logged_in'] = logged_in
    name = "Guest"
    if 'user' in request.session:
        dbsession = DBSession()
        user = request.session['user']
        try:
            dbuser = dbsession.query(User).filter_by(id=user.id).one()
            contact = dbuser.contact
            name = '%s %s' % (contact.firstname, contact.lastname)
        except NoResultFound:
            pass
    subheader = 'Welcome %s!' % name

    data = dict(
        sitescript='',
        title='Main Page',
        keywords='',
        description='',
        header="",
        subheader = subheader,
        top_bar=make_top_bar(request).render(),
        content="main content",
        left_menu='',
        footer='',
        # FIXME: get session, etc.. to work
        logged_in='')
    return data

class BaseViewer(object):
    def __init__(self, request):
        self.request = request
        self.page_data = base_data(self.request)
        # the _exception attribute is for
        # returning HTTPNotFound and like
        # responses
        self._exception = None

    def __call__(self):
        if self._exception is not None:
            return self._exception
        else:
            return self.page_data
    
    def url(self, route=None, **kw):
        if route is None:
            route = self.request.matched_route.name
        url = self.request.route_url(route, **kw)
        return url

    def link(self, value, **kw):
        url = self.url(**kw)
        return html.a(value, href=url)

    def make_menu(self, header, entries, class_='submenu'):
        menu = BaseMenu(header=header, class_=class_)
        for value, href in entries:
            menu.append_new_entry(value, href)
        return menu
    
    
    def make_left_menu(self, header, entries, class_='mainmenu'):
        menu = self.make_menu(header, entries, class_=class_)
        self.page_data['left_menu'] = menu.output()
        



        
