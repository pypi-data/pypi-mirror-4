from setuptools import setup, find_packages

version = '0.2'

long_description = (
    open('README.txt').read()
    + '\n' +
    open('CHANGES.txt').read()
    + '\n')

setup(name='five.z2monitor',
      version=version,
      description="Enable zc.monitor with Zope 2",
      long_description=long_description,
      classifiers=[
        "Programming Language :: Python",
        "License :: OSI Approved :: Zope Public License",
        "Programming Language :: Python",
        "Topic :: System :: Monitoring",
        ],
      keywords='Zope zc.monitor monitoring',
      author='Zope Corporation and contributors',
      author_email='zope-dev@zope.org',
      url='http://pypi.python.org/pypi/five.monitor',
      license='ZPL',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['five'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'zc.monitor',
          'zc.z3monitor',
          'ZODB3',
          'zope.component',
          'zope.processlifetime'
      ],
      entry_points="""
[plone.recipe.zope2instance.ctl]
monitor = five.z2monitor.zope2instance:monitor
"""
      )
