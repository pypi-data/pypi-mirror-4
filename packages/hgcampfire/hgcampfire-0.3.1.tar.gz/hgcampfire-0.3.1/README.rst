hgcampfire
==========

``hgcampfire`` provides a Mercurial hook to notify a `Campfire`_
chatroom about changesets coming in to a repository.

.. _Campfire: http://campfirenow.com

Usage
-----

Add the following to your Mercurial config (in a system, user, or
repo-level hgrc file), replacing the API key, URL, and room ID::

    [campfire]
    api_key = CAMPFIRE_AUTH_TOKEN_FOR_THE_USER_NOTIFICATIONS_WILL_COME_FROM
    url = https://myorg.campfirenow.com
    room = 123456

    [hooks]
    changegroup.campfire = python:hgcampfire.notify

These configs can of course be separated into different hgrc files,
for instance if you want to specify the Campfire data user-wide, but
apply the actual hook only to certain repositories.

.. note::

    Beginning in September 2010, the Campfire API began requiring SSL, so
    the "url" setting in your config should be an https:// url.

Customization
-------------

You can modify the template ``hgcampfire`` uses for its notification
by setting the ``template`` config value in the ``[campfire]``
section. The default value is ``{user} pushed:\n{changesets}``. This
template has the following context available to it: ``root`` is the
repository root path, ``user`` is the value of the ``$USER``
environment variable, and ``changesets`` is the list of changesets
pushed.

You can also modify the template ``hgcampfire`` uses to report each
changeset, by setting the ``cset_template`` config value in the
``[campfire]`` section. This should be a Mercurial changeset template,
of the same form you'd pass to --template. The default value is
``* "{desc}" by {author}``.

You can also choose to exclude certain types of changesets from the
notifications.  By default all commits will be included in the notification.
Within the ``[campfire]`` section you can set the following properties::

    only_branch=default
    include_nonmerges=False
    include_merges_of_one_branch=False
    include_merges_of_two_branches=False
    exclude_merges_from_branch=<branch_regex>

The ``only_branch`` setting will only announce changesets that are on
the named branch.  By default it does not do any limiting on the branch name.
The ``include_nonmerges`` setting will include or exclude normal non-merge
changesets.  The ``include_merges_of_one_branch`` setting will include or
exclude changesets that are merges where the two parents of the merge are on
the same branch.  The ``include_merges_of_two_branches`` setting will include
or exclude changesets where the two parents of the merge are on different
branches.  By default all of the ``include_*`` are set to True.  So you
should only need to mention them in your configuration if you do not want
that type of changeset to be displayed, in which case you should set its
value to ``False``.

The ``exclude_merges_from_branch`` option takes a
regular expression and, if one is provided, will not include merges
which came from a branch with a name that matches the regular
expression.  To be more clear, it checks if the 2nd parent of the
merge commit exists on a branch whose name matches the pattern.
