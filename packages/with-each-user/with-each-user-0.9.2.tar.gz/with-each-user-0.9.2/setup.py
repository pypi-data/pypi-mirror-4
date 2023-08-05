#!/usr/bin/env python
import sys
from distutils.core import setup


def read(fname):
    try:
        return open(os.path.join(os.path.dirname(__file__), fname)).read()
    except:
        return ''

requirements = []
if sys.version_info[:2] == (2, 6):
    requirements.append('argparse')

setup(
    name='with-each-user',
    version='0.9.2',
    author='NetAngels',
    author_email='info@netangels.ru',
    scripts=['with_each_user', ],
    url='http://github.com/NetAngels/with-each-user',
    license = 'BSD',
    description = ('utility which helps to execute commands on behalf of all '
                   'users in the system in a row'),
    long_description = read('README.rst'),
    install_requires=requirements,
    classifiers=(
        'Development Status :: 4 - Beta',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Topic :: Utilities',
    )
)
