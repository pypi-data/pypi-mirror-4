from setuptools import setup, find_packages

version = '1.1'

setup(name='collective.local.addgroup',
      version=version,
      description="Allows to create a group from the sharing tab. By Ecreall",
      long_description=open("README.txt").read() + "\n" +
                       open("CHANGES.txt").read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='',
      author='Vincent Fretin',
      author_email='vincent.fretin@gmail.com',
      url='http://svn.plone.org/svn/collective/collective.local.addgroup',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective', 'collective.local'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'collective.local.adduser >= 1.1',
          'plone.app.users > 1.0.6',  # >= 1.1 for Plone 4.1, > 1.0.6 for Plone 4.0
          'plone.app.workflow >= 2.0.2',
      ],
      extras_require = {
          'test': [
              'plone.app.testing',
              'unittest2',
          ]
      },
      )
