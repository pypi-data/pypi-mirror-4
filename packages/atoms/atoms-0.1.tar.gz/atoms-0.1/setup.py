try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'Atomic data',
    'long_description': open('README.txt').read(),
    'author': 'Daniel J. Sindhikara',
    'url':'www.dansindhikara.com',
    # 'download_url':'Where to download it.',
    'author_email': 'sindhikara@gmail.com',
    'version': '0.1',
    #'install_requires': ['nose', 'numpy'], #
    'packages': ['atoms', 'atoms.tests'],
    'package_data': {"atoms.tests": ["data/*"]},
    'scripts': ['atoms/tests/atoms_tests.py'],
    'name': 'atoms',
    'license': 'LGPL'
}

setup(**config)  
