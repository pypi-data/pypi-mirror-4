from setuptools import setup, find_packages

version = '1.1.10'

setup(name='wicked',
      version=version,
      description="wicked is a compact syntax for doing wiki-like content linking and creation in zope and plone",
      long_description=open("README.txt").read() + "\n" +
                       open("CHANGES.txt").read(),
      classifiers=[
        "Framework :: Zope2",
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='wiki anti-wiki zope2 plone',
      author='whit',
      author_email='wicked@lists.openplans.org',
      url='http://pypi.python.org/pypi/wicked',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['wicked'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'zope.container',
          'zope.lifecycleevent',
          'zope.schema',
          'zope.traversing',
      ],
      entry_points="""
      [wicked.base_registration]
      basic_plone_registration = wicked.registration:BasePloneWickedRegistration
      bracketted_plone_registration = wicked.registration:BasePloneMediaWickedRegistration
      """,
      )
