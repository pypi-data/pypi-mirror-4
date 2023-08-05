import datetime
import tempfile
import unittest

from spitter import models, views, main

import sqlalchemy as sqla
from pyramid import testing
from repoze import tm
from sqlalchemy import orm


class MockQuery(list):
    def __init__(self, data={}):
        self.data = data
    def distinct(self):
        return self
    def get(self, k):
        return self.data[k]
    def from_statement(self, s):
        return self
    def all(self):
        return self.data.values()
    def order_by(self, *args, **kwargs):
        return self
    def limit(self, count):
        return self
    def first(self):
        if len(self.data) > 0:
            return self.data.values()[0]
        return None
    def __iter__(self):
        return iter(self.all())

class MockDBSession(object):
    def __init__(self, data={}):
        self.data = data
    def query(self, obj, *args, **kwargs):
        return MockQuery(self.data.get(obj, {}))
    def close(self):
        pass
    def add(self, obj):
        self.data['_added'] = self.data.get('_added', []) + [obj]
    def commit(self):
        pass
    def flush(self):
        pass

def get_dbsession(data):
    def get_dbsession(data=data):
        return MockDBSession(data)
    return get_dbsession

def setup_make_session(obj):
    obj.dbfile = tempfile.NamedTemporaryFile(suffix='.db', prefix='spitter_tests-')
    print('Creating db file: '+obj.dbfile.name)
    obj.engine = sqla.create_engine('sqlite:///'+obj.dbfile.name)
    models.Base.metadata.create_all(obj.engine)
    obj.make_session = orm.sessionmaker(bind=obj.engine,
                                        autocommit=False,
                                        autoflush=False)

def teardown_make_session(obj):
    print('Deleting db file: '+obj.dbfile.name)
    obj.dbfile.close()
    del obj.dbfile
    del obj.engine
    del obj.make_session


class ModelIntegrationTests(unittest.TestCase):
    '''An integrational base class for tests that need to do
    integration testing against a real database connection.  In most
    cases this is mostly just making sure the SQL is being run
    as expected.
    '''

    def setUp(self):
        setup_make_session(self)

        self.session = self.make_session()
        self.to_delete = []

    def tearDown(self):
        while len(self.to_delete) > 0:
            self.session.delete(self.to_delete.pop())
            self.session.flush()
        self.session.commit()
        self.session.close()
        self.session = None

        teardown_make_session(self)

    def test_following(self):
        session = self.session
        user1 = models.User('user1', 'password')
        session.add(user1)
        self.to_delete.append(user1)
        follower1 = models.User('follower1', 'password')
        session.add(follower1)
        self.to_delete.append(follower1)
        follower2 = models.User('follower2', 'password')
        session.add(follower2)
        self.to_delete.append(follower2)

        follower1.following.append(user1)
        follower2.following.append(user1)

        session.flush()

        followers = [x.username for x in user1.followers]
        assert 'follower1' in followers
        assert 'follower2' in followers


    def test_spits(self):
        session = self.session
        user1 = models.User('user1', 'password')
        session.add(user1)
        self.to_delete.append(user1)
        spit = models.Spit('user1', 'some text')
        session.add(spit)
        self.to_delete.append(spit)
        session.flush()

class SpitIntegrationTests(unittest.TestCase):
    sample_data = '''
insert into spitter_users (username, password) values ('user1', 'user1'); 
insert into spitter_users (username, password) values ('user2', 'user2'); 
insert into spitter_users (username, password) values ('user3', 'user3'); 
insert into spitter_users (username, password) values ('user4', 'user4'); 
insert into spitter_users (username, password) values ('user5', 'user5'); 
insert into spitter_user_followers (following, follower) values ('user1', 'user2');
insert into spitter_user_followers (following, follower) values ('user1', 'user3');
insert into spitter_user_followers (following, follower) values ('user1', 'user4');
insert into spitter_user_followers (following, follower) values ('user5', 'user1');
insert into spitter_user_followers (following, follower) values ('user3', 'user1');
insert into spitter_user_followers (following, follower) values ('user5', 'user2');
insert into spitter_spits (id, text, created, username) values (1, 'abc', :created, 'user3');
'''

    def setUp(self):
        setup_make_session(self)
        conn = self.engine.connect()
        created = datetime.datetime.now()
        for x in self.sample_data.split(';'):
            conn.execute(x.strip(), created=created)
        conn.close()

    def tearDown(self):
        teardown_make_session(self)

    def test_following_spits(self):
        session = self.make_session()
        user1 = session.query(models.User).get('user1')
        self.assertEqual(len(user1.following_spits), 1)
        session.close()

class ViewsTests(unittest.TestCase):

    def test_get_user(self):
        assert views.get_user(None) is None

    def test_get_active_users(self):
        data = dict([(str(x), [str(y)]) 
                     for x, y in enumerate(range(20))])
        data['abc'] = ['def']
        active_users = views.get_active_users(MockDBSession({models.User.username: data,
                                                             models.Spit.username: {'abc': ['def']}}))
        self.assertEquals(active_users,
                          ['def', '11', '10', '13', '12', '15', '14', '17', '16', '19'])

    def test_shorten(self):
        res = [x for x in views.shorten(range(5), 3)]
        self.assertEquals(res, [0, 1, 2])

    def test_users_view(self):
        req = testing.DummyRequest()
        res = views.users_view(req)
        self.assertEquals(res.location, req.application_url + '/')

    def test_add_globals(self):
        obj = {'request': {}}
        views.add_globals(obj)
        self.assertEqual(obj['username'], None)

    def test_friendly(self):
        self.assertEqual(views.friendly('abc'), u'abc')
        now = datetime.datetime.now()
        assert 'today' in views.friendly(now) 
        assert 'yesterday' in views.friendly(now-datetime.timedelta(days=1)) 
        assert 'yesterday' not in views.friendly(now-datetime.timedelta(days=10)) 

    def test_error_404(self):
        class M(object):
            message = 'Foo'
        res = views.error_404(M, None)
        assert '404' in res['error']
        assert 'Foo' in res['error']
        assert 'Sorry' in res['error_text']

    def test_error_401(self):
        class M(object):
            message = 'Foo'
        res = views.error_401(M, None)
        assert '401' in res['error']
        assert 'Foo' in res['error']
        assert 'Sorry' in res['error_text']


class RequestedViewsTests(unittest.TestCase):

    def setUp(self):
        self.request = testing.DummyRequest()
        self.data = {}
        self.request.registry.settings = {'spitter.db_session_factory': get_dbsession(self.data)}
        self._old_get_user = views.get_user
        self._old_find_session = models.find_session
        self.username = None
        views.get_user = lambda x: self.username
        db_session = MockDBSession(self.data) 
        models.find_session = lambda x: db_session
        self.request.root = models.Root(db_session)

    def tearDown(self):
        views.get_user = self._old_get_user
        models.find_session = self._old_find_session

    ## start main_view tests

    def test_unauthenticated_main_view(self):
        res = views.main_view(self.request)
        self.assertEqual(len([x for x in res['spits']]), 0)
        self.assertEqual(res['spits_type'], u'All Spits')
        self.assertEqual(res['active_users'], [])

    def test_authenticated_main_view(self):
        self.username = 'foo1'
        self.data[models.User] = {'foo1': models.User('foo1', 'foo1')}
        res = views.main_view(self.request)
        self.assertEqual(len([x for x in res['spits']]), 0)
        self.assertEqual(res['active_users'], [])

    def test_authenticated_post_main_view(self):
        self.username = 'foo1'
        self.data[models.User] = {'foo1': models.User('foo1', 'foo1')}
        self.request.method = 'POST'
        self.request.params['text'] = 'random text'
        res = views.main_view(self.request)
        self.assertEqual([x.text for x in self.data['_added']],
                         ['random text'])

    ## start users_view tests

    def test_not_following_users_view(self):
        self.username = 'foo1'
        self.data[models.User] = {'foo1': models.User('foo1', 'foo1')}
        self.request.context = models.User('bar1', 'bar1')
        res = views.user_view(self.request)
        self.assertFalse(res['following'])
        self.assertTrue(res['can_follow'])

    def test_can_follow_users_view(self):
        self.username = 'foo1'
        foo1 = models.User('foo1', 'foo1')
        self.data[models.User] = {'foo1': foo1}
        self.request.context = models.User('bar1', 'bar1')
        foo1.following = [self.request.context]
        res = views.user_view(self.request)
        self.assertTrue(res['following'])
        self.assertFalse(res['can_follow'])

    ## start user_following_view tests

    def test_user_following_view_add(self):
        self.username = 'foo1'
        bar1 = models.User('bar1', 'bar1')
        foo1 = models.User('foo1', 'foo1')
        foo1.__name__ = 'foo1'
        self.data[models.User] = {'foo1': foo1,
                                  'bar1': bar1}
        self.request.method = 'POST'
        self.request.params['came_from'] = 'http://someurl.com'

        self.request.context = foo1

        self.request.params['user'] = 'bar1'
        self.request.params['action'] = 'add'
        views.user_following_view(self.request)
        self.assertEqual([x.username for x in foo1.following],
                         ['bar1'])

    def test_user_following_view_remove(self):
        self.username = 'foo1'
        bar1 = models.User('bar1', 'bar1')
        foo1 = models.User('foo1', 'foo1')
        foo1.__name__ = 'foo1'
        self.data[models.User] = {'foo1': foo1,
                                  'bar1': bar1}
        foo1.following.append(bar1)
        self.request.method = 'POST'

        self.request.context = foo1

        self.request.params['user'] = 'bar1'
        self.request.params['action'] = 'remove'
        views.user_following_view(self.request)
        self.assertEqual([x.username for x in foo1.following], [])

    ## start login tests

    def test_bad_login(self):
        self.request.params.update({
                'came_from': 'http://someurl.com',
                'form.submitted': 1,
                'username': 'foo1',
                'password': 'baddpassword',
                })
        self.data[models.User] = {'foo1': models.User('foo1', 'foo1')}
        res = views.login(self.request)
        self.assertEqual(res['came_from'], 'http://someurl.com')
        self.assertEqual(res['error'], 'Invalid username and/or password')

    def test_good_login(self):
        self.request.params.update({
                'came_from': 'http://someurl.com',
                'form.submitted': 1,
                'username': 'foo1',
                'password': 'foo1',
                })
        self.data[models.User] = {'foo1': models.User('foo1', 'foo1')}
        res = views.login(self.request)
        self.assertEqual(res.location, 'http://someurl.com')

    def test_logout(self):
        res = views.logout(self.request)
        self.assertEqual(res.location, self.request.application_url+'/')

class ModelsTests(unittest.TestCase):

    def test_user_following_spits(self):
        user = models.User('user', 'user')
        self.assertRaises(ValueError, lambda: user.following_spits)

    def test_user_status_spit(self):
        user = models.User('user', 'user')
        self.assertRaises(ValueError, lambda: user.status_spit)

    def test_container(self):
        class Mock(object):
            __parent__ = None
        obj = Mock()
        container = models.Container(MockDBSession({obj: {'foo': obj}}), None, None)
        container.db_model = obj
        assert container['foo'] is obj
        self.assertEqual([x for x in container], [obj])

    def test_get_root(self):
        req = testing.DummyRequest()
        obj = object()
        req.registry.settings = {'spitter.db_session_factory': lambda: obj}
        root = models.get_root(req)
        assert root.db_session is obj

    def test_groupfinder(self):
        self.assertEqual(models.groupfinder(None, None), [])


class MainTests(unittest.TestCase):
    def test_init_settings(self):
        settings = main.init_settings()
        assert 'spitter.db_engine' in settings
        assert 'spitter.db_session_factory' in settings

    def test_make_app(self):
        app = main.make_app()
        assert isinstance(app, tm.TM)
