from setuptools import setup

setup(
    name = 'django-migreme',
    version = '0.0.1',
    description = 'Django Migre.me app',
    long_description = (''),
    keywords = 'django apps migreme migre.me ',
    author = 'Tracy Web Technologies',
    author_email = 'contato@tracy.com.br',
    url = 'https://github.com/TracyWebTech/django-migreme',
    download_url = 'https://github.com/TracyWebTech/django-migreme/downloads',
    license = 'BSD',
    classifiers = [
        'Environment :: Plugins',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    packages = ['migreme'],
    package_dir={'migreme': 'migreme'},
)