from setuptools import setup
from setuptools import find_packages


install_requires = [
    'setuptools',
    # -*- Extra requirements: -*-
]

entry_points = """
    # -*- Entry points: -*-
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

setup(name='example.dotdot.package',
      version='1.2',
      packages=find_packages(),
      description=("Create a custom basic Python project"),
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
      namespace_packages=['example', 
                          'example.dotdot'],
      entry_points=entry_points,
      )
