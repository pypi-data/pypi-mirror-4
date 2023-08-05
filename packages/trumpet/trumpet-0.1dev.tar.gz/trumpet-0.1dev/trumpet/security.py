from crypt import crypt
import random
from string import ascii_letters

from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from sqlalchemy.orm.exc import NoResultFound

from models.base import DBSession
from models.usergroup import User, Password

def make_salt(id=5, length=10):
    phrase = ''
    for ignore in range(length):
        phrase += random.choice(ascii_letters)
    return '$%d$%s$' % (id, phrase)

def encrypt_password(password):
    salt = make_salt()
    encrypted = crypt(password, salt)
    return encrypted

def check_password(encrypted, password):
    if '$' not in encrypted:
        raise RuntimeError, "we are supposed to be using random salt."
    ignore, id, salt, epass = encrypted.split('$')
    salt = '$%s$%s$' % (id, salt)
    check = crypt(password, salt)
    return check == encrypted


def authenticate(userid, request):
    print "called authenticate", request.params
    dbsession = DBSession()
    user = None
    try:
        user = dbsession.query(User).filter_by(username=userid).one()
    except NoResultFound:
        pass
    if user is None:
        pass
    else:
        return [g.name for g in user.groups]


def check_user_password(user, password):
    return check_password(user.pw.password, password)







authn_policy = AuthTktAuthenticationPolicy(
    secret='v3rys3cret',
    callback=authenticate)

authz_policy = ACLAuthorizationPolicy()
