import os
import urllib2
import cgi
import re
from posixpath import join

from mercurial.cmdutil import show_changeset
from mercurial.templater import templater, stringify
from mercurial.ui import util


def notify(ui, repo, node, source, url, hooktype, **kwargs):
    if hooktype not in ['changegroup', 'incoming']:
        ui.warn('Campfire Notify extension is intended only for use as changegroup or incoming hook')

    conf = HgCampfireConfig(ui)

    if conf.api_key is None or conf.campfire_url is None or conf.campfire_room is None:
        ui.warn('Campfire Notify extension requires api_key, url, and room to be set in [campfire] section of hgrc')
        return True

    revisions = get_revision_range(repo, node)
    revisions = filter_unwanted_revisions(conf, repo, revisions)

    #we may have stripped out all of the revisions
    if len(revisions) == 0:
        return False

    message = get_message_to_post(conf, ui, repo, revisions)
    post_message_to_campfire(conf, message)


def get_revision_range(repo, node):
    node_rev = repo[node].rev()
    tip_rev = repo['tip'].rev()
    return range(tip_rev, node_rev - 1, -1)


def filter_unwanted_revisions(conf, repo, revisions):
    #strip out revisions that are not on the given branch
    if conf.only_branch is not None:
        revisions = filter(lambda r: repo[r].branch() == conf.only_branch, revisions)

    #strip out merges where both parents are on same branch
    if not conf.include_single_branch_merges:
        revisions = filter(lambda r: filter_merges(True, repo, r), revisions)

    #strip out merges where the parents are on different branches
    if not conf.include_multi_branch_merges:
        revisions = filter(lambda r: filter_merges(False, repo, r), revisions)

    #strip out non merges
    if not conf.include_nonmerges:
        revisions = filter(lambda r: rev_is_merge(repo, r), revisions)

    #strip out merge if it came from a branch that matches a regex
    if conf.exclude_merges_from_branch is not None:
        expr = conf.exclude_merges_from_branch
        revisions = filter(lambda r: not parent2_branch_matches_expression(repo, r, expr), revisions)

    return revisions


def rev_is_merge(repo, rev):
    return len(repo[rev].parents()) == 2


def filter_merges(on_same_branch, repo, rev, ui=None):
    if not rev_is_merge(repo, rev):
        return True

    parents = repo[rev].parents()

    #filter single/multi-branch merges based on on_same_branch param
    if on_same_branch:
        if parents[0].branch() == parents[1].branch():
            return False
    else:
        if parents[0].branch() != parents[1].branch():
            return False
    return True


def parent2_branch_matches_expression(repo, rev, expr):
    if not rev_is_merge(repo, rev):
        return False

    parent2_branch = repo[rev].parents()[1].branch()

    match = re.search(expr, parent2_branch)
    return match is not None


def get_message_to_post(conf, ui, repo, revisions):
    displayer = show_changeset(ui, repo, {'template': conf.cset_template})
    ui.pushbuffer()
    for rev in revisions:
        displayer.show(repo[rev])
    revs = ui.popbuffer()

    user = os.environ.get('USER', 'unknown-user')
    root = repo.root
    if root.startswith(conf.strip_root_prefix):
        root = root[len(conf.strip_root_prefix):]

    t = templater(None)
    t.cache['default'] = conf.template
    return stringify(t('default', root=root, user=user, changesets=revs))


def post_message_to_campfire(conf, message):
    password_manager = urllib2.HTTPPasswordMgr()
    password_manager.add_password('Application', conf.campfire_url, conf.api_key, 'X')

    handler = urllib2.HTTPBasicAuthHandler(password_manager)
    opener = urllib2.build_opener(handler)

    target_url = join(conf.campfire_url, 'room', conf.campfire_room, 'speak.xml')

    req = urllib2.Request(target_url, "<message><body>%s</body></message>" % cgi.escape(message))
    req.add_header('Content-Type', 'application/xml')

    # Python < 2.6 raises HTTPError on a 201 status code
    try:
        response = opener.open(req)
    except urllib2.HTTPError, e:
        if not (200 <= e.code < 300):
            raise


class HgCampfireConfig(object):
    def __init__(self, ui):
        self.api_key = ui.config('campfire', 'api_key')
        self.campfire_url = ui.config('campfire', 'url')
        self.campfire_room = ui.config('campfire', 'room')
        self.cset_template = ui.config('campfire', 'cset_template', default=' * "{desc}" by {author}\n')
        self.template = ui.config('campfire', 'template', default='{user} pushed:\n{changesets}')
        self.strip_root_prefix = ui.config('campfire', 'strip_root_prefix', default='')
        self.include_single_branch_merges = util.parsebool(ui.config('campfire', 'include_single_branch_merges', default='True'))
        self.include_multi_branch_merges = util.parsebool(ui.config('campfire', 'include_multi_branch_merges', default='True'))
        self.include_nonmerges = util.parsebool(ui.config('campfire', 'include_nonmerges', default='True'))
        self.exclude_merges_from_branch = ui.config('campfire', 'exclude_merges_from_branch', default=None)
        self.only_branch = ui.config('campfire', 'only_branch', default=None)
