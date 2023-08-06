from setuptools import setup, find_packages

version = '1.1.1'

setup(name='collective.fullview',
      version=version,
      description="Alternative full view for Plone with support for BrowserViews.",
      long_description=open("README.rst").read() + "\n" +
                       open("CHANGES.rst").read(),
      classifiers=[
          "Framework :: Plone",
          "Programming Language :: Python",
      ],
      keywords='plone view',
      author='Johannes Raggam',
      author_email='raggam-nl@adm.at',
      url='http://github.com/collective/collective.fullview',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'Products.CMFCore',
          'Zope2', # For Products.Five
          'zope.publisher',
      ],
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
