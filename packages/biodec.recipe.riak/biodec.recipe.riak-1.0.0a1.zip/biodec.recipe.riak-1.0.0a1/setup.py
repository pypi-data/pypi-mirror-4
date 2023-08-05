"""Setup script."""

import os
from setuptools import setup, find_packages


def read(*rnames):
    return open(os.path.join(os.getcwd(), *rnames)).read()


setup(
    name="biodec.recipe.riak",
    version="1.0.0a1",
    author="Mauro Amico",
    author_email="mauro@biodec.com",
    description="ZC Buildout recipe for setting up Riak.",
    license="LGPL 3",
    keywords="riak zc.buildout recipe",
    url='http://pypi.python.org/pypi/biodec.recipe.riak',
    long_description=(
        read('README.md')
        + '\n' +
        read('src', 'biodec', 'recipe', 'riak', 'README.txt')
        + '\n' +
        read('CHANGES.txt')
        ),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Buildout',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        'Operating System :: POSIX',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],
    packages=find_packages('src'),
    include_package_data=True,
    package_dir={'': 'src'},
    package_data={'biodec.recipe.riak': ['README.txt']},
    namespace_packages=['biodec', 'biodec.recipe'],
    install_requires=[
        'setuptools',
        'zc.buildout',
        'zc.recipe.egg',
        ],
    extras_require={
        'test': ['zope.testing'],
    },
    entry_points={
         'zc.buildout': [
             'build = biodec.recipe.riak.build:BuildRecipe',
             'instance = biodec.recipe.riak.instance:InstanceRecipe',
         ]
    },
    zip_safe=False,
    )
