from setuptools import setup, find_packages
import os

version_file = os.path.join('on', 'caroufredsel', 'version.txt')
version = open(version_file).read().strip()

setup(name='on.caroufredsel',
      version=version,
      description="Shim to load Caroufredsel as a resource",
      long_description=open("README.rst").read() + "\n" +
                       open("CHANGES.rst").read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Framework :: Plone",
	"Framework :: Plone :: 4.2",
	"Framework :: Plone :: 4.3",
        "Programming Language :: Python",
        "Programming Language :: JavaScript",
        ],
      keywords='Caroufredsel',
      author='Toni Mueller',
      author_email='support@oeko.net',
      url='https://github.com/muellert/on.caroufredsel.git',
      license='MIT + GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['on'],
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
      extras_require = {
          'test': [
              'plone.app.testing',
          ]
      },
      )
