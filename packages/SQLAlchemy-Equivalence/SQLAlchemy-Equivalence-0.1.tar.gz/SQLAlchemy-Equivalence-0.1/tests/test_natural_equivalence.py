import sqlalchemy as sa

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy_equivalence import NaturalEquivalence


class TestCase(object):
    def setup_method(self, method):
        self.engine = create_engine('sqlite://')
        self.Base = declarative_base()
        self.Base.metadata.create_all(self.engine)

        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def teardown_method(self, method):
        self.session.close_all()
        self.Base.metadata.drop_all(self.engine)


class TestNaturalEquivalence(TestCase):
    def test_skips_primary_keys_by_default(self):
        class User(self.Base, NaturalEquivalence):
            __tablename__ = 'user'

            id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
            name = sa.Column(sa.Unicode(255))
            age = sa.Column(sa.Integer)

        user1 = User(id=1, name=u'someone')
        user2 = User(id=2, name=u'someone')
        # user1 and user2 have different primary keys, but since they use
        # natural equivalence they are equal
        assert user1 == user2

    def test_does_not_skip_natural_primary_keys(self):
        class User(self.Base, NaturalEquivalence):
            __tablename__ = 'user'

            name = sa.Column(sa.Unicode(255), primary_key=True)
            age = sa.Column(sa.Integer)

        user1 = User(name=u'someone', age=11)
        user2 = User(name=u'someone2', age=11)
        assert user1 != user2

    def test_supports_relations(self):
        class User(self.Base, NaturalEquivalence):
            __tablename__ = 'user'

            id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
            name = sa.Column(sa.Unicode(255))
            age = sa.Column(sa.Integer)

        class Article(self.Base, NaturalEquivalence):
            __tablename__ = 'article'
            id = sa.Column(sa.Integer, primary_key=True)
            created_at = sa.Column(sa.DateTime)
            author_id = sa.Column(sa.Integer, sa.ForeignKey(User.id))
            author = sa.orm.relationship(User)

        user1 = User(id=1, name=u'someone')
        user2 = User(id=2, name=u'someone')
        article1 = Article(id=1, author=user1)
        article2 = Article(id=2, author=user2)

        assert article1 == article2
