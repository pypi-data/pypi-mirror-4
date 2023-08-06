from setuptools import setup, find_packages
import os

version = '1.0.2'

setup(name='quintagroup.z3cform.captcha',
      version=version,
      description="Captcha field for z3cform based on "
                  "quintagroup.captcha.core package",
      long_description=open("README.txt").read() + "\n" +
      open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
          "Development Status :: 5 - Production/Stable",
          "Environment :: Web Environment",
          "Framework :: Plone",
          "Framework :: Plone :: 3.2",
          "Framework :: Plone :: 3.3",
          "Framework :: Plone :: 4.0",
          "Framework :: Plone :: 4.1",
          "Framework :: Plone :: 4.2",
          "Framework :: Plone :: 4.3",
          "Framework :: Zope2",
          "Framework :: Zope3",
          "License :: OSI Approved :: GNU General Public License (GPL)",
          "Operating System :: OS Independent",
          "Programming Language :: Python",
          "Topic :: Security",
          "Topic :: Software Development :: Libraries :: Python Modules",
      ],
      keywords='plone z3c form captcha',
      author='Quintagroup',
      author_email='support@quintagroup.com',
      url='http://svn.quintagroup.com/products/quintagroup.z3cform.captcha/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['quintagroup', 'quintagroup.z3cform'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'quintagroup.captcha.core',
          'z3c.form',
          # 'zope.schema',
          # 'zope.i18n',
          # 'zope.component',
          # 'zope.interface',
          # 'zope.app.pagetemplate',
          # 'Products.CMFCore',
      ],
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
