"""
Implement the package support for tooth.paste, based on Templer.
"""
import copy
from templer.core.basic_namespace import BasicNamespace
from tooth.paste.invisible import add_invisible_vars


# pylint: disable=R0904
class Package(BasicNamespace):
    """
    This creates a Python package.
    Adds invisible variables to be used by the template system.
    """
    _template_dir = 'templates/package'
    summary = "A basic namespace Python package (1 dot in name)"
    ndots = 0
    help = """
This creates a basic namespace Python package with one dot in the name.
"""
    required_templates = []
    use_cheetah = True
    vars = copy.deepcopy(BasicNamespace.vars)
    del vars[1]
    del vars[4]
    vars[1].description = 'Name of the package'

    def check_vars(self, myvars, cmd):
        myvars = super(Package, self).check_vars(myvars, cmd)
        add_invisible_vars(myvars)
        return myvars
