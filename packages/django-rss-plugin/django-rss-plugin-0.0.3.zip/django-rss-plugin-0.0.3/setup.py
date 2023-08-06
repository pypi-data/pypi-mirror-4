__author__ = 'Zhou Guangwen'
import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="django-rss-plugin",
    version="0.0.3",
    author="Guangwen Zhou",
    author_email="zgwmike@hotmail.com",
    description=("A Django CMS plugin to show django-rss-plugin."),
    license="BSD",
    keywords="django cms plugin django-rss-plugin",
    url="http://github.com/zgwmike/django-rss-plugin",
    packages=["rssplugin"],
    classifiers=[
	'Development Status :: 5 - Production/Stable',
        'Environment :: Plugins',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Topic :: Multimedia :: Video :: Display',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
    ],
    install_requires=[
	    'feedparser', 
	    'Django >= 1.4',
	    'django-cms >= 2.3'],
    long_description=read("README.rst")
)
