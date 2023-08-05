from base import baselayout


def configure_rssviewer(config, rootpath):
    config.add_route('rssviewer', '%s/{context}/{feed}' % rootpath)
    config.add_view('trumpet.views.rssviewer.MainViewer',
                    route_name='rssviewer',
                    renderer=baselayout,
                    permission='admin')
