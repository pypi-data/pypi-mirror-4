import logging
import sys

from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.config import Configurator
from pyramid_jinja2 import renderer_factory
from khufu import script, sqlahelper

from spitter import models

DEFAULT_CONNECT_STRING = 'sqlite:///spitter.db'


def init_settings(settings={}):
    settings = dict(settings)
    settings.setdefault('jinja2.directories', 'spitter:templates')
    settings.setdefault('reload_templates', True)
    settings.setdefault('spitter.db_connect_string', DEFAULT_CONNECT_STRING)
    return settings


def make_app(settings={}):
    """ This function returns a WSGI application.
    """

    settings = init_settings(settings)

    authentication_policy = AuthTktAuthenticationPolicy(
        'oursecret', callback=models.groupfinder)
    authorization_policy = ACLAuthorizationPolicy()
    config = Configurator(root_factory=models.get_root,
                          settings=settings,
                          authentication_policy=authentication_policy,
                          authorization_policy=authorization_policy)
    config.add_renderer('.html', renderer_factory)
    config.add_static_view('static', 'spitter:static')
    config.scan('spitter')

    sqlahelper.init_config(config)
    rootapp = config.make_wsgi_app()

    app = sqlahelper.with_db(rootapp, settings['spitter.db_connect_string'])

    return app


def main(argv=sys.argv[1:]):
    logging.basicConfig()

    def createtables(session):
        models.Base.metadata.create_all(session.bind)

    settings = init_settings()

    connect_string = settings['spitter.db_connect_string']
    session_factory = sqlahelper.get_session_factory(connect_string)
    commander = script.Commander([
            script.make_reloadable_server_command(make_app),
            script.make_syncdb_command(session_factory,
                                       createtables)
            ])
    commander.scan(globals())
    commander.run(argv)

if __name__ == '__main__':
    main()
