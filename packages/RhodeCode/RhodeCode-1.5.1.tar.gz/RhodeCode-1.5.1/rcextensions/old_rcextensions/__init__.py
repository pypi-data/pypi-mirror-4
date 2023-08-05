#import requests
from rhodecode.lib.compat import json

GETS = {
    'rooms': (
        'history', 'list', 'show'
    ),
    'users': (
        'list', 'show'
    )
}

POSTS = {
    'rooms': (
        'create', 'delete', 'message'
    ),
    'users': (
        'create', 'delete', 'update'
    )
}

API_VERSION = '1'
BASE_URL = 'https://api.hipchat.com/v%(version)s/%(section)s/%(method)s'


class HipChatApi(object):
    """Lightweight Hipchat.com REST API wrapper
    """
    def __init__(self, auth_token, name=None, gets=GETS, posts=POSTS,
                base_url=BASE_URL, api_version=API_VERSION):
        self._auth_token = auth_token
        self._name = name
        self._gets = gets
        self._posts = posts
        self._base_url = base_url
        self._api_version = api_version

    def _request(self, method, params={}):
        if 'auth_token' not in params:
            params['auth_token'] = self._auth_token
        url = self._base_url % {
            'version': self._api_version,
            'section': self._name,
            'method': method
        }
        if method in self._gets[self._name]:
            r = requests.get(url, params=params)
        elif method in self._posts[self._name]:
            r = requests.post(url, params=params)
        return json.loads(r.content)

    def __getattr__(self, attr_name):
        if self._name is None:
            return super(HipChatApi, self).__self_class__(
                auth_token=self._auth_token,
                name=attr_name
            )
        else:
            def wrapper(*args, **kwargs):
                return self._request(attr_name, *args, **kwargs)
            return wrapper

# Additional mappings that are not present in the pygments lexers
# used for building stats
# format is {'ext':['Names']} eg. {'py':['Python']} note: there can be
# more than one name for extension
# NOTE: that this will overide any mappings in LANGUAGES_EXTENSIONS_MAP
# build by pygments
EXTRA_MAPPINGS = {}

#==============================================================================
# WHOOSH INDEX EXTENSIONS
#==============================================================================
# if INDEX_EXTENSIONS is [] it'll use pygments lexers extensions by default.
# To set your own just add to this list extensions to index with content
INDEX_EXTENSIONS = []

# additional extensions for indexing besides the default from pygments
# those get's added to INDEX_EXTENSIONS
EXTRA_INDEX_EXTENSIONS = []


#==============================================================================
# POST CREATE REPOSITORY HOOK
#==============================================================================
# this function will be executed after each repository is created
def _crhook(*args, **kwargs):
    """
    Post create repository HOOK
    kwargs available:
     :param repo_name:
     :param repo_type:
     :param description:
     :param private:
     :param created_on:
     :param enable_downloads:
     :param repo_id:
     :param user_id:
     :param enable_statistics:
     :param clone_uri:
     :param fork_id:
     :param group_id:
     :param created_by:
    """

    return 0
CREATE_REPO_HOOK = _crhook


#==============================================================================
# POST PUSH HOOK
#==============================================================================

# this function will be executed after each push it's runned after the build-in
# hook that rhodecode uses for logging pushes
def _pushhook(*args, **kwargs):
    """
    Post push hook
    kwargs available:

      :param username: name of user who pushed
      :param ip: ip of who pushed
      :param action: pull
      :param repository: repository name
      :param pushed_revs: generator of pushed revisions
    """
#    from rhodecode.model.db import Repository
#    from rhodecode.lib import helpers as h
#    repo = Repository.get_by_repo_name(kwargs['repository'])
#    repo_url = 'https://code.appzonaut.com/%(repository)s' % kwargs
#    kwargs['repository'] = '<a href="%s">%s</a>' % (repo_url, repo.repo_name)
#
#    msg = []
#    changesets = []
#    branch = None
#    for r in kwargs['pushed_revs']:
#        cs = repo.scm_instance.get_changeset(r)
#        changesets.append(cs)
#        if branch is None:
#            branch = cs.branch
#
#    kwargs['branch'] = branch
#    msg.append("<b>%(username)s</b> pushed to %(branch)s in %(repository)s<\br>" % kwargs)
#    msg.append('<pre>')
#    for cs in changesets:
#        idurl = '<a href="%s">%s</a> \n' % (repo_url + '/changeset/' + cs.raw_id,
#                                         cs.short_id[:6])
#        msg.append('- %s (%s)' % (h.shorter(cs.message, 160), idurl))
#
#    msg.append('</pre>')
#    msg = ''.join(msg)
#    print msg

#    HIPCHAT_ROOM = "AZ - Tech"
#    HIPCHAT_TOKEN = "31a1d1678649f4715188408bf8a706"
#    HIPCHAT_FROM = "Bieber Says"
#
#    hcapi = HipChatApi(auth_token=HIPCHAT_TOKEN)
#
#    hcapi.rooms.message({
#        'room_id': HIPCHAT_ROOM,
#        'from': HIPCHAT_FROM,
#        'message': msg
#    })

    return 0
PUSH_HOOK = _pushhook


#==============================================================================
# POST PULL HOOK
#==============================================================================

# this function will be executed after each push it's runned after the build-in
# hook that rhodecode uses for logging pushes
def _pullhook(*args, **kwargs):
    """
    Post pull hook
    kwargs available::

      :param username: name of user who pulled
      :param ip: ip of who pushed
      :param action: pull
      :param repository: repository name
    """
    return 0
PULL_HOOK = _pullhook



if __name__ == '__main__':
    _pushhook()
