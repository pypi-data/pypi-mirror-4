from setuptools import setup, find_packages
import os

version = '0.5'

setup(name='collective.MockMailHost',
      version=version,
      description="Used for integration testing with Plone",
      long_description="\n".join([
          open("README.rst").read(),
          open(os.path.join("collective", "MockMailHost", "tests",
                            "SendEmail.txt")).read(),
          open(os.path.join("docs", "HISTORY.txt")).read(),
      ]),
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='',
      author='',
      author_email='',
      url='https://github.com/collective/collective.mockmailhost',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
