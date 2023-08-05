from datetime import datetime, timedelta


import feedparser

import transaction
from formencode.htmlgen import html
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import desc

from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.security import authenticated_userid


from trumpet.models.base import DBSession
from trumpet.models.rssdata import Feed, FeedData
from trumpet.security import encrypt_password

from base import base_data
from base import BaseViewer

from menus import BaseMenu



from wtforms import TextField, validators
from forms import BaseForm

valid_name = [validators.Length(min=1, max=85)]

class AddFeedForm(BaseForm):
    name = TextField('Feed Name', valid_name)
    url = TextField('Feed URL', [validators.Length(min=7, max=255)])

    
def main_data(request):
    data = base_data(request)
    maindata = dict(
        title='RSS Viewer Page',
        keywords='',
        description='',
        header="RSS Viewer Page",
        subheader="",
        content=request.matchdict['context'],
        footer=str(request.params)
        )
    data.update(maindata)
    return data

class MainViewer(BaseViewer):
    def __init__(self, request):
        BaseViewer.__init__(self, request)
        self.dbsession = DBSession()
        self.context = request.matchdict['context']
        self.page_data = main_data(request)

        # make left menu
        entries = []
        url = self.url(context='listfeeds', feed=None)
        entries.append(('View Feeds', url))
        url = self.url(context='addfeed', feed=None)
        entries.append(('Add Feed', url))
        url = self.url(context='updatefeeds', feed=None)
        entries.append(('Update Feeds', url))
        if self.context in ['viewfeed']:
            url = self.url(context='deletefeed',
                           feed=self.request.matchdict['feed'])
            entries.append(('Delete Feed', url))
        header = 'RSS View Menu'
        self.make_left_menu(header, entries)

        # make dispatch table
        self._cntxt_meth = dict(addfeed=self.add_feed,
                                listfeeds=self.list_feeds,
                                viewfeed=self.view_feed,
                                updatefeeds=self.update_feeds)
        # dispatch context request
        if self.context in self._cntxt_meth:
            self._cntxt_meth[self.context]()
        else:
            msg = 'Undefined Context: %s' % self.context
            self.page_data['content'] = '<b>%s</b>' % msg

        
    def add_feed(self):
        form = AddFeedForm(self.request.POST)
        form.add_submit("Add Feed")
        if 'submit' in self.request.params:
            self.page_data['subheader'] = 'submitted'
            if form.validate():
                transaction.begin()
                feed = Feed(form.name.data, form.url.data)
                self.dbsession.add(feed)
                self.dbsession.flush()
                transaction.commit()
            else:
                rendered = form.render(form=form, action='_addfeed_')
                self.page_data['content'] = rendered
                self.page_data['subheader'] = 'Invalid Request'
        else:
            rendered = form.render(form=form, action='_addfeed_')
            self.page_data['content'] = rendered
            self.page_data['subheader'] = 'Please add a Feed'

    def _get_latest_feed(self, feed):
        "gets latest feed in database"
        query = self.dbsession.query(FeedData).filter_by(feed_id=feed.id)
        return query.order_by(desc(FeedData.retrieved)).first()
        
    def update_feeds(self):
        query = self.dbsession.query(Feed)
        for feed in query.all():
            data = self._get_latest_feed(feed)
            data = self._update_feed(feed, data)
        self.page_data['content'] = '<h1>Feeds Updated</h1>'
        
    def list_feeds(self):
        ulist = html.ul()
        query = self.dbsession.query(Feed)
        for feed in query.all():
            vfeed = self.request.route_url('rssviewer',
                                           context='viewfeed', feed=feed.id)
            anchor = html.a(feed.name, href=vfeed)
            item = html.li(anchor)
            ulist.append(item)
        self.page_data['content'] = unicode(ulist)

    def view_feed(self):
        feed_id = self.request.matchdict['feed']
        feed = self.dbsession.query(Feed).filter_by(id=feed_id).one()
        data = self._get_latest_feed(feed)
        self._update_feed(feed, data)
        fdata = self._get_latest_feed(feed)
        content = fdata.content
        table = html.table()
        table = []
        for entry in content.entries:
            row = '<tr><td><b><a href="%s">%s</a></b></td></tr>'
            row = row % (entry.link, entry.title)
            table.append(row)
            row = '<tr><td>%s</td></tr>' % entry.summary
            table.append(row)
            if 'content' in entry:
                row = '<tr><td>%s</td></tr>' % entry.content
                table.append(row)
            if 'author' in entry:
                row = '<tr><td>%s</td></tr>' % entry.author
                table.append(row)
            row = '<tr><td>%s</td></tr>' % entry.keys()
            table.append(row)
            
        table = '<table>%s</table>' % '\n'.join(table)
        self.page_data['content'] = unicode(table)

    def _get_new_feed_data(self, feed):
        data = feedparser.parse(feed.url)
        transaction.begin()
        fdata = FeedData(feed.id, data)
        self.dbsession.add(fdata)
        self.dbsession.flush()
        transaction.commit()
        return data
    
    def _update_feed(self, feed, data):
        "take the lasted data row from rssdata and see if need to update"
        if data is not None:
            # 30 minute limit
            limit = timedelta(0, 0, 0, 0, 30)
            now = datetime.now()
            if now > data.retrieved + limit:
                self._get_new_feed_data(feed)
            else:
                diff = (data.retrieved + limit) - now
                msg = 'Still waiting %s seconds left.'
                self.page_data['subheader'] = msg % diff
        else:
            data = self._get_new_feed_data(feed)
        return data
        
