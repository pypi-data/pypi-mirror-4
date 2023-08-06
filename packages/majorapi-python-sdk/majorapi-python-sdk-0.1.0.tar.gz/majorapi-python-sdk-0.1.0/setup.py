try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'name': 'majorapi-python-sdk',
    'packages': ['majorapi'],
    'version': '0.1.0',
    'description': 'The MajorApi Python SDK',
    'license': 'MIT',
    'install_requires': ['requests'],
    'author': 'Rod Afshar',
    'author_email': 'rafshar@gmail.com',
    'url': 'http://github.com/brightmarch/majorapi-python-sdk',
    'keywords': 'majorapi',

    'classifiers': (
        'Programming Language :: Python',
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
    )
}

setup(**config)
