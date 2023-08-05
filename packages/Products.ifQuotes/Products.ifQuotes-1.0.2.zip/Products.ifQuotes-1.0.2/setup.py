from setuptools import setup, find_packages

VERSION = "1.0.2"


setup(
    description="A 'quote' content type for Plone",
    include_package_data=True,
    long_description=open("README.rst").read() + '\n' +
        open("HISTORY.txt").read(),
    maintainer="Alex Clark",
    maintainer_email="aclark@aclark.net",
    name='Products.ifQuotes',
    packages=find_packages(),
    namespace_packages=[
        'Products'
    ],
    install_requires=[
        'setuptools',
    ],
    url="https://github.com/collective/Products.ifQuotes",
    version=VERSION,
)
