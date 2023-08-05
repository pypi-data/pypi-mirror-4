import os

HERE = os.path.abspath(os.path.dirname(__file__))
NAME = 'womack'
VERSION = '0.1.1'
AUTHOR = 'Leapfrog Online'
AUTHOR_EMAIL = 'oss@leapfrogdevelopment.com'
PACKAGES = ['womack', 'womack.tests']
SCRIPTS = ['bin/womack']
DESCRIPTION = ['Womack pushes real-time javascript events from your '
               'application to clients']
LONG_DESCRIPTION = open(
    os.path.join(HERE, 'README.rst')).read()
CLASSIFIERS = [
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: BSD License',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
    'Operating System :: OS Independent',
    'Natural Language :: English',
    'Topic :: Internet :: WWW/HTTP :: HTTP Servers',
]
URL = 'https://github.com/leapfrogdevelopment/womack'
KEYWORDS = ['gevent', 'socketio', 'http', 'redis']
BASE_REQS = open(os.path.join(HERE, 'requirements.txt')).read().split()

params = dict(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    packages=PACKAGES,
    scripts=SCRIPTS,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=URL,
    classifiers=CLASSIFIERS,
    keywords=KEYWORDS,
    include_package_data=True,
    data_files = [('etc/womack',
                   ['requirements.txt', 'requirements-server.txt',
                    'requirements-docs.txt', 'requirements-test.txt']),
                  ('docs/womack', ['README.rst'])]
)


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
else:
    params['install_requires'] = BASE_REQS,
    params['entry_points'] = {
        'console_scripts': [
            'womack = womack.server:main',
            ],
        }
setup(**params)
