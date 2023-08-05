from setuptools import setup, find_packages
import os

setup(
    name='collective.portlet.actions',
    version='1.2.1',
    description="A portlet that provides the links of an action category",
    long_description=(open("README.rst").read().strip() + "\n\n" +
                      open(os.path.join("docs", "HISTORY.txt")).read().strip()),
    # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
    "Framework :: Plone :: 3.2",
    "Framework :: Plone :: 3.3",
    "Framework :: Plone :: 4.0",
    "Framework :: Plone :: 4.1",
    "Framework :: Plone :: 4.2",
    "Programming Language :: Python",
    "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords='plone portlet',
    author='Gilles Lenfant',
    author_email='gilles.lenfant@alterway.fr',
    url='http://plone.org/products/collective-portlet-actions',
    license='GPL',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['collective', 'collective.portlet'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
    'setuptools',
    # -*- Extra requirements: -*-
    'Acquisition',
    'Products.CMFCore',
    'Zope2',
    'plone.app.portlets',
    'plone.memoize',
    'plone.portlets',
    'zope.formlib',
    'zope.schema',
    ],
    extras_require={'test': ['Products.PloneTestCase']},
    entry_points="""
    # -*- Entry points: -*-
    [z3c.autoinclude.plugin]
    target = plone
    """
    )
