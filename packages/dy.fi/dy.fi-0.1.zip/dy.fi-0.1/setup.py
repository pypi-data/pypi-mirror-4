from setuptools import find_packages
from setuptools import setup

import os


long_description = (
    open(os.path.join("dy", "fi", "docs", "README.rst")).read() + "\n" +
    open(os.path.join("dy", "fi", "docs", "HISTORY.rst")).read() + "\n" +
    open(os.path.join("dy", "fi", "docs", "CONTRIBUTORS.rst")).read())


setup(
    name='dy.fi',
    version='0.1',
    description="Adds commands to checks dynamic IP address change and informs currenty IP address to dy.fi.",
    long_description=long_description,
    # Get more strings from
    # http://pypi.python.org/pypi?:action=list_classifiers
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7"],
    keywords='',
    author='Taito Horiuchi',
    author_email='taito.horiuchi@gmail.com',
    url='https://github.com/taito/dy.fi',
    license='BSD',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['dy'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools'],
    entry_points="""
    [console_scripts]
    dyfi = dy.fi:update_ip
    dyfi-last-updated =dy.fi:last_updated
    """)
