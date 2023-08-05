from setuptools import setup, find_packages

version = '0.11.5'
name = 'slapos.recipe.build'
long_description = open("README.rst").read() + "\n" + \
    open("CHANGES.txt").read() + "\n"

# extras_requires are not used because of
#   https://bugs.launchpad.net/zc.buildout/+bug/85604
setup(name=name,
      version=version,
      description="Flexible software building recipe.",
      long_description=long_description,
      classifiers=[
          "Development Status :: 2 - Pre-Alpha",
          "Framework :: Buildout :: Recipe",
          "Programming Language :: Python",
        ],
      keywords='slapos recipe',
      license='GPLv3',
      namespace_packages=['slapos', 'slapos.recipe'],
      packages=find_packages(),
      include_package_data=True,
      install_requires=[
        'setuptools', # namespaces
        'zc.buildout', # plays with buildout
        'slapos.libnetworkcache>=0.13.1', # Uses helper new in this version
        ],
      extras_require={
        'test' : ['zope.testing'],
      },
      tests_require = ['zope.testing'],
      test_suite = '%s.tests.test_suite' % name,
      zip_safe=True,
      entry_points={
        'zc.buildout': [
          'default = slapos.recipe.build:Script',
          'cmmi = slapos.recipe.build:Cmmi',
          'cpan = slapos.recipe.cpan:Cpan',
          'download = slapos.recipe.download:Recipe',
          'download-unpacked = slapos.recipe.downloadunpacked:Recipe',
          'gitclone = slapos.recipe.gitclone:Recipe',
          'npm = slapos.recipe.npm:Npm',
      ]},
    )
