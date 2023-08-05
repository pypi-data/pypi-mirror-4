import unittest

from sqlalchemy import create_engine, Column, Integer, Sequence
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.session import Session

import bottle
from bottle.ext import sqlalchemy

Base = declarative_base()

def accept_only_kwargs(route):
    def wrapper(**kwargs):
        return route(**kwargs)
    return wrapper

class Entity(Base):
    __tablename__ = 'entity'
    id = Column(Integer, Sequence('id_seq'), primary_key=True)


class AnotherPlugin(object):
    def apply(self, callback, route):
        def wrapper(*args, **kwargs):
            return callback(param=1, *args, **kwargs)
        return wrapper


class SQLAlchemyPluginTest(unittest.TestCase):

    def setUp(self):
        self.engine = create_engine('sqlite:///:memory:')
        self.app = bottle.Bottle(catchall=False)

    def test_without_metadata(self):
        sqlalchemy.Plugin(self.engine, create=False)

    def test_without_metadata_create_table_raises(self):
        plugin = sqlalchemy.Plugin(self.engine, create=True)
        self.assertRaises(bottle.PluginError, self.app.install, plugin)

    def test_with_commit(self):
        @self.app.get('/')
        def test(db):
            entity = Entity()
            db.add(entity)
            self._db = db

        self._install_plugin(self.engine, Base.metadata, create=True)
        self._request_path('/')
        self.assertEqual(self._db.query(Entity).count(), 1)

    def test_with_keyword(self):
        @self.app.get('/')
        def test(db):
            self.assertTrue(isinstance(db, Session))

        self._install_plugin(self.engine)
        self._request_path('/')

    def test_without_keyword(self):
        @self.app.get('/', sqlalchemy=dict(use_kwargs=True))
        def test():
            pass

        @self.app.get('/2')
        @accept_only_kwargs
        def test(db):
            pass

        @self.app.get('/3', sqlalchemy=dict(use_kwargs=True))
        @accept_only_kwargs
        def test(db):
            pass

        self._install_plugin(self.engine)
        self._request_path('/')
        self.assertRaises(TypeError, self._request_path, '/2')
        self._request_path('/3')

    def test_install_conflicts(self):
        self._install_plugin(self.engine)
        self._install_plugin(self.engine, keyword='db2')

        @self.app.get('/')
        def test(db, db2):
            pass

        # I have two plugins working with different names
        self._request_path('/')

    def test_route_with_view(self):
        @self.app.get('/', apply=[accept_only_kwargs])
        def test(db):
            pass

        self.app.install(sqlalchemy.Plugin(self.engine, Base.metadata))
        self._request_path('/')

    def test_route_based_keyword_config(self):
        @self.app.get('/', sqlalchemy=dict(keyword='db_keyword'))
        def test(db_keyword):
            pass

        self._install_plugin(self.engine, create=False)
        self._request_path('/')

    def test_route_based_commit_config(self):
        @self.app.get('/', sqlalchemy=dict(commit=False))
        def test(db):
            entity = Entity()
            db.add(entity)
            self._db = db

        self._install_plugin(self.engine, Base.metadata, create=True)
        self._request_path('/')
        self.assertEqual(self._db.query(Entity).count(), 0)

    def test_route_based_create_config(self):
        @self.app.get('/', sqlalchemy=dict(create=True))
        def test(db):
            entity = Entity()
            db.add(entity)

        self._install_plugin(self.engine, Base.metadata, create=False)
        self._request_path('/')

    def test_commit_on_redirect(self):
        @self.app.get('/')
        def test(db):
            entity = Entity()
            db.add(entity)
            self._db = db
            bottle.redirect('/')

        self._install_plugin(self.engine, Base.metadata, create=True)
        self._request_path('/')
        self.assertEqual(self._db.query(Entity).count(), 1)

    def test_commit_on_abort(self):
        @self.app.get('/')
        def test(db):
            entity = Entity()
            db.add(entity)
            self._db = db
            bottle.abort()

        self._install_plugin(self.engine, Base.metadata, create=True)
        self._request_path('/')
        self.assertEqual(self._db.query(Entity).count(), 0)

    def test_install_other_plugin_after(self):
        self._install_plugin(self.engine)
        self.app.install(AnotherPlugin())

        @self.app.get('/')
        def test(db, param):
            self.assertTrue(db is not None)
            self.assertEqual(param, 1)

        self._request_path('/')

    def test_install_other_plugin_before(self):
        self.app.install(AnotherPlugin())
        self._install_plugin(self.engine)

        @self.app.get('/')
        def test(db, param):
            self.assertTrue(db is not None)
            self.assertEqual(param, 1)

        self._request_path('/')

    def _request_path(self, path, method='GET'):
        self.app({'PATH_INFO': path, 'REQUEST_METHOD': method},
            lambda x, y: None)

    def _install_plugin(self, *args, **kwargs):
        self.app.install(sqlalchemy.Plugin(*args, **kwargs))


if __name__ == '__main__':
    unittest.main()
