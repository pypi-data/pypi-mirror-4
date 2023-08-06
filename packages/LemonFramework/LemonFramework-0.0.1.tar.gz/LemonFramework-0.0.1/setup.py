import os
from setuptools import setup

def read(filename):
    with open(os.path.join(os.path.dirname(__file__), filename)) as f:
        return f.read()

setup(
    name = 'LemonFramework',
    version = '0.0.1',
    author = 'Vicente Ruiz Rodríguez',
    author_email = 'vruiz2.0@gmail.com',
    description = ('Agile Web Framework.'),
    license = 'GPLv3',
    keywords = 'agile web framework',
    url = 'https://github.com/LemonFramework/LemonFramework',
    packages=['lemon', 'tests'],
    long_description=read('README.rst'),
    classifiers=[
        'Development Status :: 1 - Planning',
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Web Environment',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3',
        'Topic :: Database',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Internet :: WWW/HTTP :: Session',
        'Topic :: Internet :: WWW/HTTP :: WSGI',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
    ],
    install_requires=[],
    extras_require={
        'nosql':  ['pymongo'],
        'templates': ['jinja2'],
        'forms': ['wtforms'],
    },
)
