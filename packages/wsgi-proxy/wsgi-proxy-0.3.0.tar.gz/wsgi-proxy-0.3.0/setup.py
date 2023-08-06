from __future__ import with_statement

try:
    from setuptools import setup
    extra_options = {
        'entry_points': {
            'console_scripts': ['wsgi-proxy = wsgi_proxy.cli:main']
        },
        'install_requires': ['waitress >= 0.8.2']
    }
except ImportError:
    from distutils.core import setup
    extra_options = {
        'scripts': 'scripts/wsgi-proxy'
    }

from wsgi_proxy.version import VERSION


def readme():
    try:
        with open('README.rst') as f:
            return f.read()
    except IOError:
        pass


setup(
    name='wsgi-proxy',
    version=VERSION,
    description='WSGI proxy application',
    long_description=readme(),
    author='OSAF, Mikeal Rogers',
    author_email='mikeal.rogers' '@' 'gmail.com',
    maintainer='Hong Minhee',
    maintainer_email='minhee' '@' 'dahlia.kr',
    url='https://bitbucket.org/dahlia/wsgi-proxy',
    license='Apache License 2.0',
    packages=['wsgi_proxy'],
    platforms=['Any'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    **extra_options
)
