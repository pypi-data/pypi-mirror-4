import multiprocessing, logging
from setuptools import setup

setup(
    name = 'pyKISSmetrics',
    packages = ['KISSmetrics'],
    version = '1.0.1',
    description = 'Unofficial Python client for KISSmetrics',
    long_description = 'Unofficial Python client for KISSmetrics',
    url = 'http://github.com/shakefu/pyKISSmetrics',
    author = 'kissmetrics',
    author_email = 'support@kissmetrics.com',
    maintainer = 'Jake Alheid',
    maintainer_email = 'jacob.alheid@gmail.com',
    keywords = ['kissmetrics'],
    classifiers=[
        'Programming Language :: Python',
        'Operating System :: OS Independent',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    install_requires = [
        'urllib3',
        'pytool >= 2.1',
        ],
)
