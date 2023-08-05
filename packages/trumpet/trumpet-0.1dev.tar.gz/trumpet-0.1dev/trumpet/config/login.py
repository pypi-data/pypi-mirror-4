from base import baselayout


def configure_login(config):
    config.add_route('login', '/login')
    config.add_view('trumpet.views.login.LoginViewer',
                    route_name='login',
                    renderer=baselayout)
    config.add_route('logout', '/logout')
    config.add_view('trumpet.views.login.LoginViewer',
                    route_name='logout',
                    renderer=baselayout)
    # Handle HTTPForbidden errors with a
    # redirect to a login page.
    config.add_view('goout.views.login.login',
                    context='pyramid.httpexceptions.HTTPForbidden',
                    renderer=baselayout)


