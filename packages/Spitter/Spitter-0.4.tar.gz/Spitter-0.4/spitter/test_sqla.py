import datetime
import unittest
import sqlalchemy
from sqlalchemy import orm
import tempfile
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Note(Base):
    __tablename__ = 'notes'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    text = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    created = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False)   


class SQLAlchemyTests(unittest.TestCase):
    '''A set of tests to show that using sqlite yields different (unexpected)
    results when retrieving datetime columns when using regular session.query()
    VS session.query().from_statement().

    Currently tested with default sqlite (and bindings) that come with Python 2.7.0.

    As of this writing, test_datetime_from_query() passes but
    test_datetime_from_statement() does not.
    '''
    
    def setUp(self):
        # setup a database connection
        self.dbfile = tempfile.NamedTemporaryFile(suffix='.db', prefix='sqlite3-')
        engine = sqlalchemy.create_engine('sqlite:///'+self.dbfile.name)
        Base.metadata.create_all(engine)
        self._make_session = orm.sessionmaker(bind=engine)
        self.sessions = []

    def tearDown(self):
        for x in self.sessions:
            x.close()
        self.dbfile.close()

    def make_session(self):
        session = self._make_session()
        self.sessions.append(session)
        return session

    def setup_note_query(self, created):
        session = self.make_session()
        n = Note()
        n.text = 'foo'
        created = n.created = datetime.datetime(2010, 06, 22, 03, 14)
        session.add(n)
        session.commit()

        session = self.make_session()
        return session.query(Note)

    def test_datetime_from_query(self):
        created = datetime.datetime(2010, 06, 22, 03, 14)
        q = self.setup_note_query(created)
        self.assertEqual(q.first().created, created)

    # disabling this test as it's not really for Spitter
    # def test_datetime_from_statement(self):
    #     created = datetime.datetime(2010, 06, 22, 03, 14)
    #     q = self.setup_note_query(created)
    #     q = q.from_statement('select * from notes')
    #     self.assertEqual(q.first().created, created)
