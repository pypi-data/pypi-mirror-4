from setuptools import setup, find_packages
import os

version = '0.5'

setup(name='collective.contentrules.linguatarget',
      version=version,
      description="This package adds a custom content rule that takes the target folder's translations into account",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='syslab linguaplone linguatarget plone contentrules',
      author='JC Brand, Syslab.com GmbH',
      author_email='brand@syslab.com',
      url='http://plone.org/products/collective.contentrules.linguatarget',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective', 'collective.contentrules'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
