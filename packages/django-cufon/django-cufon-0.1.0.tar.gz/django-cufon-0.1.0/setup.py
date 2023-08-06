import re, sys
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


version = re.search("__version__ = '([^']+)'",
                    open('cufon/__init__.py').read()).group(1)


setup(
    name='django-cufon',
    version=version,
    author='Jonathan Enzinna',
    author_email='jonnyfunfun@gmail.com',
    maintainer='Jonathan Enzinna',
    maintainer_email='jonnyfunfun@gmail.com',
    url='https://github.com/JonnyFunFun/django-cufon',
    description='Cufon made easy in Django',
    long_description=open('README.rst').read(),
    classifiers=['Development Status :: 4 - Beta                 ',
                 'Environment :: Web Environment',
                 'Framework :: Django',
                 'Intended Audience :: Developers',
                 'License :: OSI Approved :: GNU General Public License (GPL)',
                 'Natural Language :: English',
                 'Operating System :: OS Independent',
                 'Programming Language :: Python :: 2.6',
                 'Programming Language :: Python :: 2.7',
                 'Topic :: Utilities'],
    license='GPLv3',
    keywords=['cufon','django'],
    packages=['cufon'],
    package_data={'': ['COPYING'], 'tpy': ['*.cfg']},
    zip_safe=False
)