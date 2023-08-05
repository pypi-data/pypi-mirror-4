from setuptools import find_packages
from setuptools import setup

import os


setup(
    name='plone.formwidget.datetime',
    version='1.0b1',
    description="Datetime widgets for Plone",
    long_description=open("README.rst").read() + "\n" +
        open(os.path.join("docs", "HISTORY.rst")).read(),
    # Get more strings from
    # http://pypi.python.org/pypi?:action=list_classifiers
    classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
    ],
    keywords='plone date time datetime event widget archetypes z3c.form',
    author='Plone Foundation',
    author_email='plone-developers@lists.sourceforge.net',
    url='https://github.com/collective/plone.formwidget.datetime',
    license='GPL',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['plone', 'plone.formwidget'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'mock',
        'plone.app.jquerytools',
        'setuptools',
        'unittest2',
        'z3c.form',
        'zope.app.testing',
        'zope.i18nmessageid',
        ],
        extras_require=dict(
            z3cform=[
                'z3c.form',
                'zope.i18n',
            ],
            archetypes=[
                'Products.Archetypes',
                'Products.CMFCore',
                'Zope2',
            ],
            test=[
                'Products.Archetypes',
                'Products.CMFCore',
                'Products.GenericSetup',
                'Zope2',
                'plone.app.testing',
                'profilehooks',
                'z3c.form',
                'zc.buildout',
                'lxml',
                'zope.testing',
            ],
        ),
)
