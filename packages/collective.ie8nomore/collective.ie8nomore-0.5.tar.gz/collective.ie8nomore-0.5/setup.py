from setuptools import setup, find_packages
import os

version = '0.5'

long_description = (
    open('README.txt').read() + '\n' +
    open(os.path.join('docs', 'CONTRIBUTORS.txt')).read() + '\n' +
    open(os.path.join('docs', 'CHANGES.txt')).read() + '\n')

setup(name='collective.ie8nomore',
      version=version,
      description="Plone viewlet to prompt users to upgrade to a better web browser.",
      long_description=long_description,
      classifiers=[
        "Development Status :: 4 - Beta",
        "Framework :: Plone",
        "Framework :: Plone :: 4.1",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Natural Language :: English",
        "Natural Language :: Spanish",
        ],
      keywords='plone internet explorer',
      author='Noe Nieto',
      author_email='nnieto@noenieto.com',
      url='https://github.com/collective/collective.ie8nomore',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'Products.CMFPlone',
          'plonetheme.sunburst'
      ],
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
