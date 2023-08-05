from setuptools import find_packages
from setuptools import setup

import os


long_description = (
    open("README.rst").read() + "\n" +
    open(os.path.join("collective", "cart", "core", "docs", "INSTALL.rst")).read() + "\n" +
    open(os.path.join("collective", "cart", "core", "docs", "HISTORY.rst")).read() + "\n" +
    open(os.path.join("collective", "cart", "core", "docs", "CONTRIBUTORS.rst")).read() + "\n" +
    open(os.path.join("collective", "cart", "core", "docs", "CREDITS.rst")).read())


setup(
    name='collective.cart.core',
    version='0.5.2',
    description="Yet another cart for Plone.",
    long_description=long_description,
    # Get more strings from
    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Framework :: Plone",
        "Framework :: Plone :: 4.2",
        "Framework :: Plone :: 4.3",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7"],
    keywords='',
    author='Taito Horiuchi',
    author_email='taito.horiuchi@gmail.com',
    url='https://github.com/collective/collective.cart.core/',
    license='BSD',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['collective', 'collective.cart'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'collective.behavior.salable',
        'five.grok',
        'hexagonit.testing',
        'plone.app.contentlisting',
        'plone.app.dexterity',
        'plone.app.portlets',
        'plone.directives.form',
        'setuptools',
        'zope.i18nmessageid'],
    entry_points="""
    # -*- Entry points: -*-

    [z3c.autoinclude.plugin]
    target = plone
    """)
