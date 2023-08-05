from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import Unicode
from sqlalchemy import ForeignKey


from sqlalchemy.orm import relationship

from base import Base

# imports for populate()
import transaction
from sqlalchemy.exc import IntegrityError
from base import DBSession

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(Unicode(50), unique=True)
    email = Column(Unicode(50), unique=True)
    pw = relationship('Password', uselist=False)

    def __init__(self, username):
        self.username = username

    def __repr__(self):
        return self.username

class Password(Base):
    __tablename__ = 'passwords'
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    password = Column(Unicode(150))
    
    def __init__(self, user_id, password):
        self.user_id = user_id
        self.password = password


class Group(Base):
    __tablename__ = 'groups'
    id = Column(Integer, primary_key=True)
    name = Column(Unicode(50))

    def __init__(self, name):
        self.name = name

class UserGroup(Base):
    __tablename__ = 'group_user'
    group_id = Column(Integer, ForeignKey('groups.id'), primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)

    def __init__(self, gid, uid):
        self.group_id = gid
        self.user_id = uid
        


User.groups = relationship(Group, secondary='group_user')

def populate_groups():
    transaction.begin()
    session = DBSession()
    groups = ['user', 'admin', 'guest', 'manager']
    for gname in groups:
        group = Group(gname)
        session.add(group)
    session.flush()
    transaction.commit()
    
def populate_users():
    from trumpet.security import encrypt_password
    transaction.begin()
    session = DBSession()
    users = ['admin']
    # Using id_count to presume
    # the user's id, which should work
    # when filling an empty database.
    id_count = 0
    for uname in users:
        id_count += 1
        user = User(uname)
        password = encrypt_password(uname)
        session.add(user)
        pw = Password(id_count, password)
        session.add(pw)
    session.flush()
    transaction.commit()
    

def populate_usergroups():
    transaction.begin()
    session = DBSession()
    users = [(1,1)] # admin
    admins = [(1,1)] # admin
    all = users + admins
    for gid, uid in all:
        row = UserGroup(gid, uid)
        session.add(row)
    session.flush()
    transaction.commit()


def populate():
    popfuns = [populate_groups, populate_users,
               populate_usergroups]
    for pfun in popfuns:
        try:
            pfun()
        except IntegrityError:
            transaction.abort()

