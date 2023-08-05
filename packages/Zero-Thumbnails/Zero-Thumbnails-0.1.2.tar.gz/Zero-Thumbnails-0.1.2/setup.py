from os.path import abspath, dirname, join, normpath

from setuptools import find_packages, setup


setup(

    # Basic package information:
    name = 'Zero-Thumbnails',
    version = '0.1.2',
    packages = find_packages(),

    # Packaging options:
    zip_safe = False,
    include_package_data = True,

    # Package dependencies:
    install_requires = ['Django>=1.3.1', 'South>=0.7.3', 'zero-common', 
                        'PIL>=1.1.7'],

    # Metadata for PyPI:
    author = 'Jose Maria Zambrana Arze',
    author_email = 'contact@josezambrana.com',
    license = 'apache license v2.0',
    url = 'http://github.com/mandlaweb/Zero-Thumbnails',
    keywords = 'zero thumbnails',
    description = 'App to add and manage thumbnails into a model',
    long_description = "App to add thumbnails management to your project."
)

