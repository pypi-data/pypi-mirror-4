import re

import transaction
from docutils.core import publish_parts

from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.security import authenticated_userid
from pyramid.view import view_config

from trumpet.models.base import DBSession
from trumpet.models.wiki import Page

from base import base_data, BaseViewer

# regular expression used to find WikiWords
wikiwords = re.compile(r":\b([A-Z]\w+[A-Z]+\w+)")

EDIT_PAGE_FORM = """<form action="%s" method="post">
          <textarea name="body" rows="10"
                    cols="60">%s</textarea><br/>
          <input type="submit" name="form.submitted" value="Save">
        </form>"""

def _anchor(href, value):
    return '<a href="%s">%s</a>' % (href, value)

def main_data(request):
    data = base_data(request)
    maindata = dict(
        title='Main Page',
        keywords='',
        description='',
        header='Main Page',
        subheader="System Administration",
        footer="footer",
        left_menu='<a href="/wiki/MainPlan">main plan</a>',
        top_bar='<a href="/">home</a><br/><a href="/wiki/listpages">list</a>'
        )
    data.update(maindata)
    return data


def main_view(request):
    data = main_data(request)
    return data

    
def view_wiki(request):
    location = request.route_url('view_page', pagename='FrontPage')
    return HTTPFound(location=location)

def view_page(request):
    pagename = request.matchdict['pagename']
    session = DBSession()
    page = session.query(Page).filter_by(name=pagename).first()
    if page is None:
        location = request.route_url('add_page', pagename=pagename)
        return HTTPFound(location=location)

    def check(match):
        word = match.group(1)
        exists = session.query(Page).filter_by(name=word).all()
        if exists:
            url = request.route_url('view_page', pagename=word)
        else:
            url = request.route_url('add_page', pagename=word)
        return _anchor(url, word)

    content = publish_parts(page.content, writer_name='html')['html_body']
    content = wikiwords.sub(check, content)
    edit_url = request.route_url('edit_page', pagename=pagename)
    logged_in = authenticated_userid(request)
    maindata = main_data(request)
    maindata['maincontent'] = content
    maindata['footer'] = '<a href="%s">edit page</a>' % edit_url
    maindata['title'] = page.name
    maindata['main_header'] = page.name
    return maindata

def add_page(request):
    name = request.matchdict['pagename']
    if 'form.submitted' in request.params:
        session = DBSession()
        body = request.params['body']
        page = Page(name, body)
        session.add(page)
        location = request.route_url('view_page', pagename=name)
        return HTTPFound(location=location)
    save_url = request.route_url('add_page', pagename=name)
    page = Page('', '')
    logged_in = authenticated_userid(request)
    maindata = main_data(request)
    return dict(page=page, save_url=save_url, logged_in=logged_in)

def edit_page(request):
    name = request.matchdict['pagename']
    session = DBSession()
    page = session.query(Page).filter_by(name=name).one()
    if 'form.submitted' in request.params:
        page.content = request.params['body']
        session.add(page)
        location = request.route_url('view_page', pagename=name)
        return HTTPFound(location=location)
    save_url = request.route_url('edit_page', pagename=name)
    logged_in = authenticated_userid(request)
    return dict(page=page, save_url=save_url, logged_in=logged_in)




class WikiViewer(BaseViewer):
    def __init__(self, request):
        BaseViewer.__init__(self, request)
        self.route = self.request.matched_route.name
        self.page_data.update(main_data(self.request))
        # dispatch table
        self._cntxt_meth = dict(view_wiki=self.view_wiki,
                                view_page=self.view_page,
                                add_page=self.add_page,
                                edit_page=self.edit_page,
                                list_pages=self.list_pages)
        # dispatch on route name
        if self.route in self._cntxt_meth:
            self._cntxt_meth[self.route]()
        else:
            msg = "Unhandled route %s" % self.route
            self.page_data['content'] = '<b>%s</b>' % msg
            


    def _anchor(self, href, value):
        return '<a href="%s">%s</a>' % (href, value)

    def view_wiki(self):
        location = self.request.route_url('view_page', pagename='FrontPage')
        self._exception = HTTPFound(location=location)

    def view_page(self):
        pagename = self.request.matchdict['pagename']
        session = DBSession()
        page = session.query(Page).filter_by(name=pagename).first()
        if page is None:
            location = self.url(route='add_page', pagename=pagename)
            self._exception = HTTPFound(location=location)
            return
        def check(match):
            word = match.group(1)
            exists = session.query(Page).filter_by(name=word).all()
            if exists:
                url = self.url(route='view_page', pagename=word)
            else:
                url = self.url(route='add_page', pagename=word)
            return self._anchor(url, word)
        # this is a sad "markup" system
        # good for a tutorial, but needs to be better
        # for actual use.
        content = publish_parts(page.content, writer_name='html')['html_body']
        content = wikiwords.sub(check, content)

        edit_url = self.url(route='edit_page', pagename=pagename)
        # We should check the session here
        # this is from tutorial, but we need better
        # solution.
        logged_in = authenticated_userid(self.request)
        self.page_data['content'] = content
        self.page_data['footer'] = self._anchor(edit_url, "Edit Page")
        self.page_data['title'] = page.name
        self.page_data['header'] = page.name

    def _add_new_page(self, name):
        transaction.begin()
        session = DBSession()
        body = self.request.params['body']
        page = Page(name, body)
        session.add(page)
        transaction.commit()

    def add_page(self):
        name = self.request.matchdict['pagename']
        if 'form.submitted' in self.request.params:
            self._add_new_page(name)
            location = self.url(route='view_page', pagename=name)
            self._exception = HTTPFound(location=location)        
            return
        save_url = self.url(route='add_page', pagename=name)
        page = Page(name, '')
        logged_in = authenticated_userid(self.request)
        self.page_data['content'] = EDIT_PAGE_FORM % (save_url, '')
        
        
    def edit_page(self):
        name = self.request.matchdict['pagename']
        session = DBSession()
        page = session.query(Page).filter_by(name=name).one()
        if 'form.submitted' in self.request.params:
            page.content = self.request.params['body']
            transaction.begin()
            session.add(page)
            transaction.commit()
            location = self.url(route='view_page', pagename=name)
            self._exception = HTTPFound(location=location)
            return
        save_url = self.url(route='edit_page', pagename=name)
        logged_in = authenticated_userid(self.request)
        self.page_data['content'] = EDIT_PAGE_FORM % (save_url, page.content)

    def list_pages(self):
        session = DBSession()
        pages = session.query(Page).all()
        pagelist = []
        for page in pages:
            url = self.url(route='view_page', pagename=page.name)
            anchor = self._anchor(url, page.name)
            pagelist.append('<li>%s</li>' % anchor)
        ul = '<ul>%s</ul>' % '\n'.join(pagelist)
        self.page_data['content'] = ul
        
