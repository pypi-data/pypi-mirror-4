import os
from setuptools import setup, find_packages

name = 'zc.recipe.deployment'

entry_points = '''
[zc.buildout]
default = %(name)s:Install
deployment = %(name)s:Install
configuration = %(name)s:Configuration
crontab = %(name)s:Crontab
sharedconfig = %(name)s:SharedConfig

[zc.buildout.uninstall]
default = %(name)s:uninstall
sharedconfig = %(name)s:uninstall_shared_config

''' % globals()

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(
    name = name,
    version='0.10.0',
    author = 'Jim Fulton',
    author_email = 'jim@zope.com',
    description = 'ZC Buildout recipe for Unix deployments',
    license = 'ZPL 2.1',
    keywords = 'deployment build',
    url = 'http://www.python.org/pypi/' + name,
    long_description = (
    read('README.txt')
    + '\n' +
    read('CHANGES.txt')
    + '\n' +
    'Detailed Documentation\n'
    '**********************\n'
    + '\n' +
    read('src', 'zc', 'recipe', 'deployment', 'README.txt')
    + '\n' +
    'Download\n'
    '**********************\n'
    ),

    install_requires = ['setuptools'],
    extras_require = {
        'test': [
            'zc.buildout',
            'zope.testing',
            ]},
    entry_points = entry_points,
    package_dir = {'': 'src'},
    packages = find_packages('src'),
    namespace_packages = ['zc', 'zc.recipe'],
    zip_safe = False,
    include_package_data = True,
    )

