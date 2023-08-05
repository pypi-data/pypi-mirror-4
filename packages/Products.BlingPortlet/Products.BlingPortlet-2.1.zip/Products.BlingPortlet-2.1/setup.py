from setuptools import setup, find_packages
import os

version = open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 
    'Products', 'BlingPortlet', 'version.txt')).read().strip()

setup(name='Products.BlingPortlet',
    version=version,
    description="A portlet that adds bling to your site",
    long_description=open("README.txt").read() + "\n" +
                     open("HISTORY.txt").read(),
    # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
      "Framework :: Plone",
      "Programming Language :: Python",
      "Topic :: Software Development :: Libraries :: Python Modules",
      ],
    keywords='',
    author='WebLion Documentation Group, Penn State University',
    author_email='support@weblion.psu.edu',
    url='http://weblion.psu.edu/',
    license='GPL',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['Products'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
      'setuptools',
      'Products.CMFPlone',
      # -*- Extra requirements: -*-
      ],
    extras_require = {
      'test': ['mocker','Products.CMFTestCase'],
    },
    entry_points="""
      # -*- Entry points: -*-
      """,
    )
