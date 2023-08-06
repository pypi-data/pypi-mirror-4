from setuptools import find_packages
from setuptools import setup

import os


long_description = (
    open("README.rst").read() + "\n" +
    open(os.path.join("src", "collective", "cart", "core", "docs", "INSTALL.rst")).read() + "\n" +
    open(os.path.join("src", "collective", "cart", "core", "docs", "HISTORY.rst")).read() + "\n" +
    open(os.path.join("src", "collective", "cart", "core", "docs", "CONTRIBUTORS.rst")).read() + "\n" +
    open(os.path.join("src", "collective", "cart", "core", "docs", "CREDITS.rst")).read())


setup(
    name='collective.cart.core',
    version='0.6',
    description="Yet another cart for Plone.",
    long_description=long_description,
    classifiers=[
        "Framework :: Plone",
        "Framework :: Plone :: 4.2",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7"],
    keywords='',
    author='Taito Horiuchi',
    author_email='taito.horiuchi@gmail.com',
    url='https://github.com/collective/collective.cart.core/',
    license='BSD',
    packages=find_packages('src', exclude=['ez_setup']),
    package_dir={'': 'src'},
    namespace_packages=['collective', 'collective.cart'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'Products.CMFPlone',
        'collective.base',
        'collective.behavior.salable',
        'five.pt',
        'hexagonit.testing',
        'plone.app.dexterity',
        'plone.directives.form',
        'setuptools'],
    entry_points="""
    # -*- Entry points: -*-

    [z3c.autoinclude.plugin]
    target = plone
    """)
