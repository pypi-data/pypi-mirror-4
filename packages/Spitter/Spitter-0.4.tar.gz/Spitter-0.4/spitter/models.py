import datetime

import sqlalchemy as sqla
from sqlalchemy import orm
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import session as sqla_session


def find_session(obj):
    return sqla_session.Session.object_session(obj)

Base = declarative_base()

user_followers = sqla.Table(
    'spitter_user_followers',
    Base.metadata,
    sqla.Column('following', sqla.String,
                sqla.ForeignKey('spitter_users.username')),
    sqla.Column('follower', sqla.String,
                sqla.ForeignKey('spitter_users.username'))
    )


class User(Base):
    __tablename__ = 'spitter_users'
    username = sqla.Column(sqla.String, primary_key=True)
    password = sqla.Column(sqla.String, nullable=False)

    following = orm.relationship(
        'User', user_followers,
        primaryjoin=username == user_followers.c.follower,
        secondaryjoin=username == user_followers.c.following,
        passive_deletes=True)
    followers = orm.relationship(
        'User', user_followers,
        primaryjoin=username == user_followers.c.following,
        secondaryjoin=username == user_followers.c.follower,
        passive_deletes=True)

    spits = orm.relationship('Spit', order_by='spitter_spits.c.created.desc()')

    def __init__(self, username, password):
        self.username = username
        self.password = password

    @property
    def following_spits(self):
        session = find_session(self)
        if session is None:
            raise ValueError('%s object is no longer attached '
                             'to an open session' % str(self))

        sql = ("select id, username, created, text from spitter_spits "
               "where username in (select following from "
               "spitter_user_followers "
               "where follower='%s') or username='%s' order by created desc"
               % (self.username, self.username))
        return session.query(Spit).from_statement(sql).all()

    @property
    def status_spit(self):
        session = find_session(self)
        if session is None:
            raise ValueError('%s object is no longer '
                             'attached to an open session' % str(self))

        q = session.query(Spit).order_by(Spit.created.desc())
        spit = q.limit(1).first()
        return spit

    def __str__(self):
        return '<User %s>' % self.username
    __repr__ = __str__


class Spit(Base):
    __tablename__ = 'spitter_spits'

    id = sqla.Column(sqla.Integer, primary_key=True)
    text = sqla.Column(sqla.String, nullable=False)
    created = sqla.Column(sqla.DateTime, nullable=False)
    username = sqla.Column(sqla.String,
                           sqla.ForeignKey(User.username),
                           nullable=False)

    def __init__(self, username, text):
        self.text = text
        self.username = username
        self.created = datetime.datetime.now()


class Container(object):

    def __init__(self, db_session, name, parent):
        self.db_session = db_session
        self.__name__ = name
        self.__parent__ = parent

    def __getitem__(self, k):
        obj = self.db_session.query(self.db_model).get(k)
        obj.__parent__ = self
        obj.__name__ = str(k)
        return obj

    def __iter__(self):
        q = self.db_session.query(self.db_model)
        return (x for x in q)


class UserContainer(Container):
    db_model = User


class SpitContainer(Container):
    db_model = Spit

    def __iter__(self):
        q = self.db_session.query(self.db_model).order_by(Spit.created.desc())
        return (x for x in q)


class Root(dict):

    __name__ = None
    __parent__ = None

    def __init__(self, db_session):
        self.db_session = db_session
        self['u'] = UserContainer(db_session, 'u', self)
        self['s'] = SpitContainer(db_session, 's', self)


def get_root(request):
    return Root(request.db)


def groupfinder(userid, request):
    return []
