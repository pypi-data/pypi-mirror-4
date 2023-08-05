from setuptools import setup, find_packages
import os

version = '1.0'

setup(name='cs.recipe.checkinterval',
      version=version,
      description="Buildout recipe that calculates the python-check-interval value for your zope instance",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Framework :: Buildout :: Recipe",
        "Framework :: Zope2",
        "Programming Language :: Python",
        ],
      keywords='python zope interpreter check interval',
      author='Mikel Larreategi',
      author_email='mlarreategi@codesyntax.com',
      url='http://github.com/codesyntax/cs.recipe.checkinterval',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['cs', 'cs.recipe'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'jarn.checkinterval'
      ],
      entry_points={
            'zc.buildout': ['default = cs.recipe.checkinterval:Recipe'],
            },
      )
