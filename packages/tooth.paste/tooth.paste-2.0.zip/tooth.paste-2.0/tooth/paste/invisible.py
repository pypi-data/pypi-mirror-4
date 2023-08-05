"""
This is the tooth.paste Python module.
"""
from templer.core.vars import StringVar
import os

from templer.core.vars import EASY
from templer.core.vars import EXPERT


class InvisibleStringVar(StringVar):
    """
    A StringVar that is not used for user input, but stored a value for
    use in the templates.
    """
    def __repr__(self):
        return self.default

    def __str__(self):
        return self.default


def add_invisible_vars(myvars):
    """
    Add some invisible variables that don't appear on the interactive command
    line. There are only used for easy insertion into templates.
    """

    myvars['long_description'] = InvisibleStringVar(
        'long_description',
        title='Long Description',
        description='Multi-line description (in ReST)',
        default='',
        modes=(),
        page='Metadata',
        help="""
This should be a full description for your project. It will be
used in the egg's setup.py.

It should be entered in 'restructured text' format; for information,
see http://docutils.sourceforge.net/rst.html).
""")

    myvars['travisci'] = InvisibleStringVar(
        'travisci',
        title='Travis-CI',
        description='Travis-Ci',
        default='.travis.yml',
        modes=(EASY, EXPERT),
        page='Metadata',
        help="""
Travis-CI
""")

    myvars['travisci_user'] = InvisibleStringVar(
        'travisci_user',
        title='Travis-CI User',
        description='Travis-CI User',
        modes=(EASY, EXPERT),
        page='Metadata',
        help="""
Travis-CI URL
""")

    myvars['travisci_project'] = InvisibleStringVar(
        'travisci_project',
        title='Travis-CI Project',
        description='Travis-CI Project',
        default=os.environ.get('USER', 'travisci_project'),
        modes=(EASY, EXPERT),
        page='Metadata',
        help="""
Travis-CI Project
""")

    info = (myvars['travisci_user'], myvars['travisci_project'])
    myvars['travisci_url'] = InvisibleStringVar(
        'travisci_url',
        title='Travis-CI URL',
        description='Travis-CI URL',
        default="https://secure.travis-ci.org/%s/%s" % info,
        modes=(EASY, EXPERT),
        page='Metadata',
        help="""
Travis-CI URL
""")

    myvars['documentation_url'] = InvisibleStringVar(
        'documentation_url',
        title='documentation_url',
        description='documentation_url',
        default="",
        modes=(EASY, EXPERT),
        page='Metadata',
        help="""
documentation_url
""")

    myvars['staticdotempty'] = InvisibleStringVar(
        'staticdotempty',
        title='staticdotempty',
        description='staticdotempty',
        default=".empty",
        modes=(EASY, EXPERT),
        page='Metadata',
        help="""
staticdotempty
""")

    myvars['repository_url'] = InvisibleStringVar(
        'repository_url',
        title='repository_url',
        description='repository_url',
        default="",
        modes=(EASY, EXPERT),
        page='Metadata',
        help="""
repository_url
""")

    myvars['zopeskel'] = InvisibleStringVar(
        'zopeskel',
        title='ZopeSkel',
        description='ZopeSkel',
        default='.zopeskel',
        modes=(EASY, EXPERT),
        page='Metadata',
        help="""
ZopeSkel
""")
    return myvars
