import os

from setuptools import find_packages
from setuptools import setup

project = 'kotti_contentpreview'
version = '0.1'

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
CHANGES = open(os.path.join(here, 'CHANGES.rst')).read()

setup(
    name=project,
    version=version,
    description="Content preview in Kotti's contents view",
    long_description=README + '\n\n' + CHANGES,
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Pylons",
        "Framework :: Pyramid",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: User Interfaces",
    ],
    keywords='kotti theme',
    author='Marco Scheidhuber',
    author_email='j23d@jusid.de',
    url='https://github.com/j23d/kotti_contentpreview',
    license='BSD-derived (http://www.repoze.org/LICENSE.txt)',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'Kotti>=0.9a1',
        'kotti_settings>=0.1a4',
    ],
    entry_points={
        'fanstatic.libraries': [
            'kotti_contentpreview = kotti_contentpreview.fanstatic:library',
        ],
    },
)
