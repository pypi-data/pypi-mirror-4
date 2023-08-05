import datetime

from spitter import models

from pyramid import security, interfaces as pyraifaces
from pyramid.events import subscriber
from pyramid.exceptions import NotFound, Forbidden
from pyramid.httpexceptions import HTTPFound
from pyramid.url import model_url
from pyramid.view import view_config


def get_user(request):
    return security.authenticated_userid(request)


def friendly(obj):
    if isinstance(obj, datetime.datetime):
        return friendly(obj.date()) + ' - ' + friendly(obj.time())
    elif isinstance(obj, datetime.date):
        diff = datetime.datetime.today().date() - obj
        if diff.days == 0:
            return 'today'
        elif diff.days == 1:
            return 'yesterday'
        return obj.strftime('%b %d, %Y')
    elif isinstance(obj, datetime.time):
        return obj.strftime('%I:%M%p').lower()
    elif isinstance(obj, basestring):
        try:
            # doing this hack due to the fact that sqlite will reeturn
            # unicode objects in place of datetime columns on sql models
            # in certain circumstances
            dt = datetime.datetime.strptime(obj, '%Y-%m-%d %H:%M:%S.%f')
            return friendly(dt)
        except ValueError:
            return unicode(obj)
    return unicode(obj)


def shorten(data, count=10):
    for x, item in enumerate(data):
        if x > count - 1:
            break
        yield item


def get_active_users(db_session):
    # find users that have created spits
    active_users = db_session.query(models.Spit.username).distinct()
    active_users = [x[0] for x in shorten(active_users)]

    # not enough active users? find some random users from the database
    if len(active_users) < 10:
        for record in db_session.query(models.User.username).distinct():
            if record[0] not in active_users:
                active_users.append(record[0])
            if len(active_users) >= 10:
                break

    return active_users


@subscriber(pyraifaces.IBeforeRender)
def add_globals(event):
    event['username'] = get_user(event['request'])
    event['friendly'] = friendly


@view_config(context=models.Root,
             renderer='main.html')
def main_view(request):
    username = get_user(request)

    res = {}
    if username is not None:
        if request.method == 'POST':
            spit = models.Spit(get_user(request),
                               request.params['text'])
            request.db.add(spit)
            request.db.flush()

        user = request.db.query(models.User).get(username)
        res['spits'] = user.following_spits
        res['following'] = [x.username for x in user.following]
        res['status_spit'] = user.status_spit
    else:
        res['spits'] = request.root['s']
        res['spits_type'] = u'All Spits'

    res['spits'] = shorten(res['spits'])
    res['active_users'] = get_active_users(request.db)

    return res


@view_config(context=models.UserContainer)
def users_view(request):
    return HTTPFound(location=model_url(request.root, request))


@view_config(context=models.User,
             renderer='user.html')
def user_view(request):
    username = get_user(request)

    user = None
    if username is not None:
        user = request.db.query(models.User).get(username)

    context_user = request.context

    res = {'spits': request.context.spits,
           'following': False,
           'can_follow': False,
           'status_spit': context_user.status_spit}

    if user is not None and user.username != context_user.username:
        if request.context.username in [x.username for x in user.following]:
            res['following'] = True
            res['can_follow'] = False
        else:
            res['can_follow'] = True

    return res


@view_config(context=models.User,
             name="following")
def user_following_view(request):
    if request.method == 'POST':
        action = request.params.get('action')
        follower = request.db.query(models.User).get(request.context.username)
        to_follow = request.db.query(models.User).get(request.params['user'])
        if action == 'add':
            follower.following.append(to_follow)
        elif action == 'remove':
            for x, obj in enumerate(follower.following):
                if obj.username == to_follow.username:
                    del follower.following[x]
                    break
        request.db.flush()

    if 'came_from' in request.params:
        return HTTPFound(location=request.params['came_from'])
    return HTTPFound(location=model_url(request.context, request))


@view_config(name='login',
             renderer='login.html',
             context=models.Root)
def login(request):
    came_from = request.params.get('came_from',
                                   model_url(request.root, request))

    message = ''
    if 'form.submitted' in request.params:
        username = request.params.get('username', None)
        password = request.params.get('password', '')

        user = request.db.query(models.User).get(username)
        if user is not None and user.password == password:
            return HTTPFound(location=came_from,
                             headers=security.remember(request, username))
        message = 'Invalid username and/or password'

    return {'came_from': came_from,
            'error': message}


@view_config(name='logout',
             context=models.Root)
def logout(request):
    headers = security.forget(request)
    return HTTPFound(location=model_url(request.root, request),
                     headers=headers)


@view_config(context=NotFound,
             renderer='error.html')
def error_404(context, request):
    error = '404 - Not Found'
    if context.message:
        error += ' - ' + context.message
    return {'error': error,
            'error_text': ('Sorry but the requested '
                           'resource could not be found')}


@view_config(context=Forbidden,
             renderer='error.html')
def error_401(context, request):
    error = '401 - Forbidden'
    if context.message:
        error += ' - ' + context.message
    return {'error': error,
            'error_text': ('Sorry but you do not '
                           'have access to the requested resource')}
