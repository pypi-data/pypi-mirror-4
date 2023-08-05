"""
Unit tests for the tooth.paste Python module.
"""
from tooth.paste.tooth_basic_namespace import ToothBasicNamespace
from tooth.paste.tooth_basic_namespace import InvisibleStringVar

try:
    import unittest2 as unittest  # pylint: disable=F0401
except ImportError:
    import unittest  # NOQA


# pylint: disable=R0904
class TestToothBasicNamespace(unittest.TestCase):
    """
    Unit test for the ToothBasicNamespace class.
    """

    def test_initialization(self):
        """
        Check the initialization of the ToothBasicNamespace class.
        """
        tooth = ToothBasicNamespace('name')
        template_dir = 'templates/tooth_nested_namespace'
        # pylint: disable=W0212
        self.failUnless(tooth._template_dir == template_dir)
        self.failUnless(tooth.summary == "A custom basic Python project")
        self.failUnless(tooth.help == """
This creates a Tooth Python project.
""")
        self.failUnless(tooth.required_templates == [])
        self.failUnless(tooth.use_cheetah is True)

    def test_check_vars(self):
        """
        Call the check_vars method.
        """
        # pylint: disable=W0232, C0111, R0903
        class DummyOptions:
            options = []
            templates = []
            no_interactive = True

        # pylint: disable=W0232, C0111, R0903
        class DummyCmd:
            _deleted_once = 0
            options = DummyOptions
            interactive = False
        cmd = DummyCmd()
        tooth = ToothBasicNamespace('name')
        myvars = {'project': 'project'}
        myvars = tooth.check_vars(myvars, cmd)
        self.failUnless(myvars['namespace_package'] == 'project')
        self.failUnless(str(myvars['repository_url']) == '')
        self.failUnless(myvars['description'] == '')
        self.failUnless(myvars['package'] == 'project')
        self.failUnless(myvars['author_email'] == '')
        self.failUnless(myvars['license_name'] == 'gpl')
        self.failUnless(myvars['author'] == '')
        self.failUnless(str(myvars['documentation_url']) == '')
        travisci_url = 'https://secure.travis-ci.org//mroder'
        self.failUnless(str(myvars['travisci_url']) == travisci_url)
        self.failUnless(str(myvars['zopeskel']) == '.zopeskel')
        self.failUnless(myvars['project'] == 'project')
        url = 'http://svn.plone.org/svn/collective/'
        self.failUnless(myvars['url'] == url)
        self.failUnless(str(myvars['travisci_user']) == '')
        self.failUnless(myvars['version'] == '1.0')
        self.failUnless(myvars['zip_safe'] is False)
        self.failUnless(myvars['keywords'] == '')
        self.failUnless(str(myvars['travisci_project']) == 'mroder')
        self.failUnless(str(myvars['travisci']) == '.travis.ci')
        self.failUnless(myvars['long_description'] == '')
        self.failUnless(myvars['expert_mode'] == 'easy')


# pylint: disable=R0904
class TestInvisibleStringVar(unittest.TestCase):
    """
    Unit test for the InvisibleStringVar class.
    """

    def test_repr_without_default(self):
        """
        __repr__ should return empty string by default
        """
        invisible = InvisibleStringVar('name', 'desc')
        self.failUnless(invisible.__repr__() == '')

    def test_repr_with_default(self):
        """
        __repr__ should return the default value string when it is set.
        """
        invisible = InvisibleStringVar('name', 'desc', default="default")
        self.failUnless(invisible.__repr__() == 'default')

    def test_str_without_default(self):
        """
        __str__ should return empty string by default
        """
        invisible = InvisibleStringVar('name', 'desc')
        self.failUnless(invisible.__str__() == '')

    def test_str_with_default(self):
        """
        __str__ should return the default value string when it is set.
        """
        invisible = InvisibleStringVar('name', 'desc', default="default")
        self.failUnless(invisible.__str__() == 'default')
