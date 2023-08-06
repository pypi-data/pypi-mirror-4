try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'Serieskeeper - Remember what you have started and finished',
    'author': 'Charles Nodell',
    'url': 'https://bitbucket.org/cnodell/serieskeeper/overview',
    'download_url': 'https://bitbucket.org/cnodell/serieskeeper/downloads/',
    'author_email': 'cnodell@simplesparks.com',
    'version': 'v0.0.0',
    'install_requires': [],
    'packages': ['serieskeeper'],
    'scripts': ['sk'],
    'name': 'serieskeeper',
    'classifiers': [
        "Programming Language :: Python",
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Other/Nonlisted Topic",
        ]
}

setup(**config)
