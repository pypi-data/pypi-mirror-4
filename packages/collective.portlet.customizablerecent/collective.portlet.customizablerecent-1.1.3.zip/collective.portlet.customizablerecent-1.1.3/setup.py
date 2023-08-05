from setuptools import setup, find_packages

version = '1.1.3'

setup(name='collective.portlet.customizablerecent',
      version=version,
      description="A recent items portlet with parameters",
      long_description=open("README.txt").read() + "\n" +
                       open("CHANGES.txt").read() + "\n" +
                       open("docs/INSTALL.txt").read(),
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='portlets',
      author='Thomas Desvenain',
      author_email='thomasdesvenain@ecreall.com',
      url='http://pypi.python.org/pypi/collective.portlet.customizablerecent',
      license='GPL',
      packages=find_packages(),
      namespace_packages=['collective', 'collective.portlet'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'plone.app.portlets > 2.0.1',
      ],
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
