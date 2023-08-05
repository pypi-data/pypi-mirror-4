try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
    
config = {
    'description': 'My Bananas project. Learning how to use project skeletons and make packages.',
    'author': 'Huyen Tran',
    'url': 'http://pypi.python.org/pypi/Bananas/',
    'download_url': 'http://pypi.python.org/pypi/Bananas/',
    'author_email': 'hey.huyen@gmail.com',
    'version': '0.1.2',
    'install_requires': ['nose'],
    'packages': ['banana'],
    'scripts': ['bin/this-is-bananas.py'],
    'long-description': open('README.txt').read(),
    'name': 'Bananas'
}

setup(**config)