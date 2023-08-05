"""
Oisin Mulvihill
2012-01-19
"""
from setuptools import setup, find_packages

Name='evasion-common'
ProjectUrl="http://github.com/oisinmulvihill/evasion-common/tarball/master#egg=evasion_common"
Version='1.0.2'
Author='Oisin Mulvihill'
AuthorEmail='oisinmulvihill at gmail dot com'
Maintainer=' Oisin Mulvihill'
Summary='Helper functions collected together from other evasion modules to aid reuse such as get_free_port() and wait_for_ready().'
License='Evasion Project CDDL License'
ShortDescription=Summary

try:
    fd = open("README.rst","r")
    Description = fd.read()
    fd.close()
except IOError:
    Description=Summary


needed = [
]

EagerResources = [
    'evasion',
]

ProjectScripts = [
]

PackageData = {
    '': ['*.*'],
}

EntryPoints = """
"""


setup(
    url=ProjectUrl,
    name=Name,
    zip_safe=False,
    version=Version,
    author=Author,
    author_email=AuthorEmail,
    description=ShortDescription,
    long_description=Description,
    license=License,
    scripts=ProjectScripts,
    install_requires=needed,
    setup_requires=[
      'nose>=1.0.0',
      'coverage'
    ],
    test_suite="nose.collector",
    entry_points=EntryPoints,
    packages=find_packages('lib'),
    package_data=PackageData,
    package_dir = {'': 'lib'},
    eager_resources = EagerResources,
    namespace_packages = ['evasion'],
)
