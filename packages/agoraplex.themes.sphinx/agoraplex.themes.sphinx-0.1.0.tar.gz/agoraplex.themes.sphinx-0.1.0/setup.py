from distribute_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages

from agoraplex.themes.sphinx import __version__

setup(
    name='agoraplex.themes.sphinx',
    version=__version__,
    author='Tripp Lilley',
    author_email='tripplilley@gmail.com',
    keywords='sphinx extension theme agoraplex',

    packages=[
        'agoraplex',
        'agoraplex.themes',
        'agoraplex.themes.sphinx',
        ],
    namespace_packages=[
        'agoraplex',
        'agoraplex.themes',
        ],
    include_package_data=True,
    zip_safe=False,

    install_requires=['sphinx>=1.1'],

    url='https://github.com/agoraplex/themes',
    license='See LICENSE.rst',
    description='A Sphinx theme for Agoraplex projects, based on the Pylons Sphinx theme',
    long_description=open('README.rst').read(),

    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.7",
        "Topic :: Documentation",
        "Topic :: Software Development :: Documentation",
        ]
)
