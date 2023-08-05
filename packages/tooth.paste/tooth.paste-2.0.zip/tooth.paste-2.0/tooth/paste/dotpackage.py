"""
Implement the basic namespace support for tooth.paste, based on Templer.
"""
from templer.core.basic_namespace import BasicNamespace
from tooth.paste.invisible import add_invisible_vars


# pylint: disable=R0904
class DotPackage(BasicNamespace):
    """
    This creates a basic name space Python package with one dot in the name.
    Adds invisible variables to be used by the template system.
    """
    _template_dir = 'templates/dotpackage'
    summary = "A basic namespace Python package (1 dot in name)"
    ndots = 1
    help = """
This creates a basic namespace Python package with one dot in the name.
"""
    required_templates = []
    use_cheetah = True

    def check_vars(self, myvars, cmd):
        myvars = super(DotPackage, self).check_vars(myvars, cmd)
        add_invisible_vars(myvars)
        return myvars
