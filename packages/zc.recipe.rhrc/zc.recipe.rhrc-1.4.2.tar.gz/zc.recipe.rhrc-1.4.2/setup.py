import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description=(
        read('README.txt')
        + '\n' +
        'Detailed Documentation\n'
        '**********************\n'
        + '\n' +
        read('src', 'zc', 'recipe', 'rhrc', 'README.txt')
        + '\n' +
        'Download\n'
        '**********************\n'
        )

entry_points = '''
[zc.buildout]
default=zc.recipe.rhrc:Recipe

[zc.buildout.uninstall]
default=zc.recipe.rhrc:uninstall
'''

name = 'zc.recipe.rhrc'
setup(
    name = name,
    version = '1.4.2',
    author = 'Jim Fulton',
    author_email = 'jim@zope.com',
    description = 'ZC Buildout recipe for Redhat RC scripts',
    long_description = long_description,
    license = 'ZPL 2.1',
    keywords = 'buildout',

    entry_points=entry_points,
    packages = find_packages('src'),
    namespace_packages = ['zc', 'zc.recipe'],
    package_dir = {'': 'src'},
    extras_require = dict(
        test=[
            'zc.buildout',
            'zope.testing',
            ]),
    install_requires = 'setuptools',
    zip_safe = False,
    )
