import os
from setuptools import setup
from setuptools import find_packages

README = open(os.path.join(os.path.dirname(__file__), 'README')).read()

os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name = 'django-embed',
    version = '0.2',
    packages = find_packages(),
    include_package_data = True,
    license = 'MIT License',
    description = 'A simple Django app to generate embed code from youtube, twitter and slideshare.',
    long_description = README,
    url = 'http://mejorando.la/',
    author = 'https://github.com/mejorandola',
    author_email = 'd@mejorando.la',
    install_requires = ['requests==0.14.2', 'requests-oauth==0.4.1'],
    keywords='Embed youtube twitter slideshare python',
    classifiers = [
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)