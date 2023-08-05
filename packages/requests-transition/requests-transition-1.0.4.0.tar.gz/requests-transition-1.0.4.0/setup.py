#!/usr/bin/env python
import os
import sys

#: Python 2.x?
is_py2 = (sys.version_info[0] == 2)

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

BASEDIR = os.path.dirname(__file__)

os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
packages = [
    'requests1',
    'requests1.packages',
	'requests1.packages.charade',
    'requests1.packages.urllib3',
    'requests1.packages.urllib3.packages',
    'requests1.packages.urllib3.packages.ssl_match_hostname',
    'requests0',
    'requests0.packages',
    'requests0.packages.urllib3',
    'requests0.packages.urllib3.packages',
    'requests0.packages.urllib3.packages.ssl_match_hostname'
]

if is_py2:
    packages.extend([
        'requests0.packages.oauthlib',
        'requests0.packages.oauthlib.oauth1',
        'requests0.packages.oauthlib.oauth1.rfc5849',
        'requests0.packages.oauthlib.oauth2',
        'requests0.packages.oauthlib.oauth2.draft25',
        'requests0.packages.chardet',
    ])
else:
    packages.append('requests0.packages.chardet2')

requires = []

setup(
    name='requests-transition',
    version='1.0.4.0',
    description="Python HTTP for busy people who don't have time to resolve version conflicts yet.",
    long_description=open(os.path.join(BASEDIR, 'README.rst')).read(),
    author='Rob Speer',
    author_email='rob@luminoso.com',
    url='https://github.com/LuminosoInsight/python-requests-transition',
    packages=packages,
    package_data={'': ['LICENSE', 'NOTICE'], 'requests0': ['*.pem'], 'requests1': ['*.pem']},
    package_dir={'requests0': 'version0/requests',
                 'requests1': 'version1/requests'},
    include_package_data=True,
    install_requires=requires,
    license=open(os.path.join(BASEDIR, 'LICENSE')).read(),
    zip_safe=False,
    classifiers=(
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        # 'Programming Language :: Python :: 3.0',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
    ),
)

del os.environ['PYTHONDONTWRITEBYTECODE']
