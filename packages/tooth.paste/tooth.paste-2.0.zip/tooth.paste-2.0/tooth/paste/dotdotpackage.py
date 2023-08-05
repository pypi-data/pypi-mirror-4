"""
Implement the nested namespace support for tooth.paste, based on Templer.
"""
import copy

from tooth.paste.dotpackage import DotPackage

from templer.core.base import get_var
from templer.core.nested_namespace import VAR_NS2


# pylint: disable=R0904
class DotDotPackage(DotPackage):
    """
    This creates a nested namespace Python package with two dots in the name.
    """
    _template_dir = 'templates/dotdotpackage'
    summary = "A nested namespace Python package (2 dots in name)"
    ndots = 2
    help = """
This creates a nested namespace Python package with two dots in the name.
"""
    required_templates = []
    use_cheetah = True

    vars = copy.deepcopy(DotPackage.vars)
    get_var(vars, 'namespace_package').default = 'my'
    vars.insert(2, VAR_NS2)
    get_var(vars, 'package').default = 'example'
