from setuptools import setup, find_packages
import sys
sys.path.insert(0, './src')
from dm import __version__

import platform

# Need to map through str because some versions of Python 2.6 return ints.
pythonVersion = '.'.join(map(str, platform.python_version_tuple()[:2]))

install_requires = []
# Something funny happens with FormEncode and SQLObject 1.0.0.
install_requires.append('SQLObject==1.2.3')
#if pythonVersion != '2.5':
#    # Psycopg v2.4.2 breaks SQLObject autoCommit feature.
#    install_requires.append('psycopg2==2.4')
install_requires.append('markdown>=1.7, <=2.2.1')
install_requires.append('django>=1.0,<=1.1.4')
if pythonVersion == '2.5':
    install_requires.append('pysqlite')
    install_requires.append('simplejson')

setup(
    name = 'domainmodel',
    version = __version__,
    package_dir = { '' : 'src' },
    packages = find_packages('src'),
    scripts = ['bin/domainmodel-makeconfig', 'bin/domainmodel-admin', 'bin/domainmodel-test'],
    zip_safe = False,
    include_package_data = True,
    install_requires = install_requires,
    # Metadata for upload to PyPI.
    author = 'Appropriate Software Foundation, Open Knowledge Foundation',
    author_email = 'kforge-dev@lists.okfn.org',
    license = 'AGPL',
    url = 'http://appropriatesoftware.net/domainmodel/Home.html',
    description = 'Toolkit for domain model-based enterprise application frameworks.',
    long_description = \
"""
DomainModel provides a toolkit for domain model-based enterprise application frameworks.

Please refer to the Features page of the domainmodel website for more information.

http://appropriatesoftware.net/domainmodel/Home.html

""",
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)

