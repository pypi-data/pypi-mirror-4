from setuptools import setup, find_packages

import content_links


setup(
    name='content-links',
    packages=find_packages(),
    include_package_data=True,
    version=content_links.__version__,
    description='',
    long_description=open('README.rst').read(),
    author=content_links.__author__,
    author_email='admin@incuna.com',
    url='https://github.com/incuna/content-links/',
    install_requires=[],
    zip_safe=False,
)
