from setuptools import setup, find_packages

setup(name='collective.contentrules.mailtorole',
      version='1.5',
      description="Send e-mail to users having a role on the object",
      long_description=(open("README.txt").read() + "\n" +
                        open("CHANGES.rst").read()),
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
          "Framework :: Plone",
          "Framework :: Plone :: 3.2",
          "Framework :: Plone :: 3.3",
          "Framework :: Plone :: 4.0",
          "Framework :: Plone :: 4.1",
          "Framework :: Plone :: 4.2",
          "Programming Language :: Python",
          "Topic :: Software Development :: Libraries :: Python Modules",
          ],
      keywords='plone contentrules action mail',
      author='Zest Software (Fred van Dijk)',
      author_email='info@zestsoftware.nl',
      url='http://plone.org/products/collective.contentrules.mailtorole',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective', 'collective.contentrules'],
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
      )
