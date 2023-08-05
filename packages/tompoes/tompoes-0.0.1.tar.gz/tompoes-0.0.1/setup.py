from setuptools import setup, find_packages


__version__ = "0.0.1"


setup(
    # package name in pypi
    name='tompoes',
    # extract version from module.
    version=__version__,
    description="Tom is een poes en hij is lief.",
    long_description="(Heel lief zelfs)",
    classifiers=[],
    keywords='',
    author='Lars van de Kerkhof',
    author_email='lars@permanentmarkers.nl',
    url='',
    license='',
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
