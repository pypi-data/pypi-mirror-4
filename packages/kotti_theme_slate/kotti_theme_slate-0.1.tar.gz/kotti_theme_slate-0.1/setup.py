import os

from setuptools import find_packages
from setuptools import setup

project = 'kotti_theme_slate'
version = '0.1'

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
CHANGES = open(os.path.join(here, 'CHANGES.rst')).read()

setup(
    name=project,
    version=version,
    description="Slate Theme from http://bootswatch.com/slate/ for Kotti",
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
    author='Andreas Kaiser',
    author_email='disko@binary-punks.com',
    url='https://github.com/disko/kotti_theme_slate',
    license='BSD',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'Kotti',
    ],
    entry_points={
        'fanstatic.libraries': [
            'kotti_theme_slate = kotti_theme_slate:library',
        ],
    },
)