import os
from setuptools import setup

README = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name = 'django-dublincore',
    version = '0.1',
    packages = ['dublincore'],
    include_package_data = True,
    license = 'BSD License - see LICENSE file', 
    description = 'A simple Django app to attach Dublin Core metadata to arbitrary Django objects',
    long_description = README,
    author = 'Mark Redar',
    author_email = 'mredar@gmail.com',
    url = 'https://github.com/mredar/django-dublincore',
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
