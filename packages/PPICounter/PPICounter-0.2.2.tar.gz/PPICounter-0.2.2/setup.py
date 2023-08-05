try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'PPI Calculator',
    'author': 'Gabor',
    'url': 'URL to get at it',
    'download_url': 'Where to download it.',
    'author_email': 'My email',
    'version': '0.2.2',
    'install_requirements': ['nose'],
    'packages': ['converter', 'bin'],
    'scripts': ['bin/ppi'],
    'name': 'PPICounter'
}

setup(**config)
