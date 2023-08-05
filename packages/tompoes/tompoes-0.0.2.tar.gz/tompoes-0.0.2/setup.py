"""
It is impossible to properly install this package in buildout 1.6.x.

This package installs fine with pip.

::

    >>> pip install tompoes
    >>> tom
    setup(script=['bin/tom']) works!
    >>> tom_main
    entry_points console_scripts works!

However it is not possible to properly install it in a buildout.

::

    >>> python bootstrap.py
    >>> ./bin/buildout -v
    >>> ./bin/tom
    -bash: ./bin/tom: No such file or directory
    >>> ./bin/tom_main
    Traceback (most recent call last):
      File "./bin/tom_main", line 29, in <module>
        import tompoes
    ImportError: No module named tompoes

    Seems like a problem in buildout.easy_install.


"""
from setuptools import setup, find_packages


__version__ = "0.0.2"


setup(
    # package name in pypi
    name='tompoes',
    # extract version from module.
    version=__version__,
    description="It is impossible to properly install this package in buildout 1.6.x.",
    long_description=__doc__,
    classifiers=[],
    keywords='',
    author='Lars van de Kerkhof',
    author_email='lars@permanentmarkers.nl',
    url='',
    license='Public Domain',
    # include all packages in the egg, except the test package.
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    # include non python files
    include_package_data=True,
    zip_safe=False,
    # specify dependencies
    install_requires=[
        'distribute',
    ],
    # generate scripts
    entry_points={
        'console_scripts':[
            'tom_main = tompoes:main',
        ]
    },
    scripts=[
        'scripts/tom',
    ],
)
