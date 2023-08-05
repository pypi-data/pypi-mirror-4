from base import baselayout


def configure_wiki(config, rootpath):
    config.add_route('view_wiki', rootpath)
    config.add_view('trumpet.views.wiki.WikiViewer',
                    route_name='view_wiki',
                    renderer=baselayout)
    config.add_route('list_pages', '%s/listpages' % rootpath)
    config.add_view('trumpet.views.wiki.WikiViewer',
                    route_name='list_pages',
                    renderer=baselayout)
    config.add_route('view_page', '%s/{pagename}' % rootpath)
    config.add_view('trumpet.views.wiki.WikiViewer',
                    route_name='view_page',
                    renderer=baselayout)
    config.add_route('add_page', '%s/add_page/{pagename}' % rootpath)
    config.add_view('trumpet.views.wiki.WikiViewer',
                    route_name='add_page',
                    renderer=baselayout,
                    permission='wiki_add')
    config.add_route('edit_page', '%s/{pagename}/edit_page' % rootpath)
    config.add_view('trumpet.views.wiki.WikiViewer',
                    route_name='edit_page',
                    renderer=baselayout,
                    permission='wiki_edit')
    
