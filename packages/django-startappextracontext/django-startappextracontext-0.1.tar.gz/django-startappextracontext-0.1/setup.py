from setuptools import setup, find_packages
import os
import platform

DESCRIPTION = """A small django app that provides an enhanced startapp management command. 
              An extra parameter called extra_context is supplied to allow for more flexible 
              app templates."""

LONG_DESCRIPTION = None
try:
    LONG_DESCRIPTION = open('README.md').read()
except:
    pass

CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Framework :: Django',
]

setup(
    name='django-startappextracontext',
    version='0.1',
    packages=find_packages(),
    author=u'S\xe6var \xd6fj\xf6r\xf0 Magn\xfasson',
    author_email='saevar@saevar.is',
    url='http://github.com/saevarom/startappextracontext',
    license='MIT',
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    platforms=['any'],
    classifiers=CLASSIFIERS,
    zip_safe=False,
    include_package_data=True,
)
