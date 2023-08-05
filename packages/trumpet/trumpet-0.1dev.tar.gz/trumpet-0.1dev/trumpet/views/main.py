from datetime import datetime

from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.security import authenticated_userid

from trumpet.models.base import DBSession

from base import NotFound, base_data, make_top_bar
from base import BaseViewer
from menus import BaseMenu


def make_main_menu(request, data):
    menu = BaseMenu(header='Main Menu', class_='submenu')
    userid = data['logged_in']
    if userid:
        url = request.route_url('user', context='password',
                                userid=userid)
        menu.append_new_entry('Change Password', url)
        url = request.route_url('user', context='status',
                                userid=userid)
        menu.append_new_entry('Status', url)
    else:
        login_url = request.route_url('login')
        menu.append_new_entry('Sign In', login_url)
    if 'user' in request.session:
        user = request.session['user']
        if user.role == 'admin':
            url = request.route_url('admin', context='main')
            menu.append_new_entry('admin', url)
    url = request.route_url('view_wiki')
    menu.append_new_entry('wiki', url)
    url = request.route_url('rssviewer', context='listfeeds', feed=None)
    menu.append_new_entry('rss', url)
    return menu

def main_data(request):
    data = base_data(request)
    mainmenu = make_main_menu(request, data)
    top_bar = make_top_bar(request)
    maindata = dict(title='Main Page',
                    header='Main Page',
                    top_bar=top_bar.render(),
                    left_menu=mainmenu.output())
    data.update(maindata)
    return data

class MainViewer(BaseViewer):
    def __init__(self, request):
        BaseViewer.__init__(self, request)

        # make left menu
        entries = []
        userid = None
        if 'logged_in' in request.session:
            userid = request.session['logged_in']
        if userid is None:
            url = request.route_url('view_wiki')
            entries.append(('wiki', url))
            url = request.route_url('rssviewer', context='listfeeds', feed=None)
            entries.append(('rss', url))
        else:
            url = request.route_url('login')
            entries.append(('Sign In', url))
        header = 'Main Menu'
        self.make_left_menu(header, entries)

        



