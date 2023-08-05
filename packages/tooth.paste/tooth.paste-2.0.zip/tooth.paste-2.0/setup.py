from setuptools import setup
from setuptools import find_packages


install_requires = [
    'setuptools',
    # -*- Extra requirements: -*-
    'PasteScript',
    'templer.core',
]

entry_points = """
    # -*- Entry points: -*-
    [paste.paster_create_template]
    package = tooth.paste:Package
    dotpackage = tooth.paste:DotPackage
    dotdotpackage = tooth.paste:DotDotPackage
    """

classifiers = [
    'Programming Language :: Python',
    # Get more strings from
    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
]

with open("README.txt") as f:
    README = f.read()

with open("CHANGES.txt") as f:
    CHANGES = f.read()

setup(name='tooth.paste',
      version='2.0',
      packages=find_packages(),
      description=("Create shiny new Python packages with Sphinx documentation,"
                   " unit tests and tools to keep your code clean"),
      long_description=README + '\n' + CHANGES,
      author='Maik Roder',
      author_email='maikroeder@gmail.com',
      include_package_data=True,
      zip_safe=False,
      classifiers=classifiers,
      install_requires=install_requires,
      keywords='Tooth, paste',
      url='https://github.com/maikroeder/tooth.paste.git',
      license='gpl',
      namespace_packages=['tooth'],
      entry_points=entry_points,
      )
