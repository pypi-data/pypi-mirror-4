from setuptools import setup, find_packages
import os

version = '1.2'

setup(name='simplelayout.portlet.dropzone',
      version=version,
      description="Plone portlet with a simplelayout dropzone.",
      long_description=open("README.rst").read() + "\n" + \
          open(os.path.join("docs", "HISTORY.txt")).read(),

      # Get more strings from
      # http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],

      keywords='',
      author='4teamwork GmbH',
      author_email='mailto:info@4teamwork.ch',
      url='https://github.com/4teamwork/simplelayout.portlet.dropzone',
      license='GPL2',

      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['simplelayout', 'simplelayout.portlet'],
      include_package_data=True,
      zip_safe=False,

      install_requires=[
        'setuptools',
        'plone.app.portlets',
        'simplelayout.base'
        # -*- Extra requirements: -*-
        ],

      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
