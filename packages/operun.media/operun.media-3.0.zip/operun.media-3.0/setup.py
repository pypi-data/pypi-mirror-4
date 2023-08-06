from setuptools import setup, find_packages
import os

version = '3.0'

setup(name='operun.media',
      version=version,
      description="A product to integrate any type of media to Plone",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='Plone Audio Video Media',
      author='operun.de by Stefan Antonelli',
      author_email='info@operun.de',
      url='https://github.com/starzel/operun.media',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['operun'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      extras_require = {
        'test': [
            'plone.app.testing',
            'plone.act',
            'robotsuite',
            'robotframework-selenium2library',
            ]
      },
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
