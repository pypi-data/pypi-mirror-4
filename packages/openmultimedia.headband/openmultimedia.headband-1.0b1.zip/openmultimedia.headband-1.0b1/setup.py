from setuptools import setup, find_packages
import os

version = '1.0b1'
description = "This package defines an editable viewlet to add an image \
headband for the site."
long_description = open("README.txt").read() + "\n" + \
                   open(os.path.join("docs", "INSTALL.txt")).read() + "\n" + \
                   open(os.path.join("docs", "CREDITS.txt")).read() + "\n" + \
                   open(os.path.join("docs", "HISTORY.txt")).read()

setup(name='openmultimedia.headband',
      version=version,
      description=description,
      long_description=long_description,
      classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: 4.1",
        "Framework :: Plone :: 4.2",
        "Framework :: Plone :: 4.3",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='plone viewlet editable',
      author="Juan Pablo Gimenez",
      author_email='jpg@rosario.com',
      url='https://github.com/OpenMultimedia/openmultimedia.headband',
      license='GPLv2',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      namespace_packages=['openmultimedia', ],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'plone.app.layout',
          'plone.app.registry',
          'plone.registry',
          'Products.CMFCore',
          'Products.CMFPlone',
          'Products.statusmessages',
          'setuptools',
          'z3c.form',
      ],
      extras_require={
          'test': [
              'interlude',
              'plone.app.testing',
              'plone.testing',
              'unittest2',
          ]
      },
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
