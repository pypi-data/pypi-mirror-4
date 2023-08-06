from setuptools import setup, find_packages

version = '1.0a4'

setup(name='collective.portlet.banners',
      version=version,
      description="A portlet to rotate clickable banners.",
      long_description=open("README.txt").read() + "\n" +
                       open("CHANGES.txt").read(),
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='Plone portlet banner rotating image sponsor logo',
      author='Matt Yoder',
      author_email='mattyoder@groundwire.org',
      url='http://svn.plone.org/svn/collective/collective.portlet.banners/trunk',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective', 'collective.portlet'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'plone.app.blob',
          'setuptools',
      ],
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
