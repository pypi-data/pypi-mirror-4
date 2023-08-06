from setuptools import setup, find_packages

readme = open('README.txt').read().strip()
history = open('CHANGES.rst').read().strip()
long_description = "%s\n\n\n%s" % (readme, history)

setup(name='collective.editskinswitcher',
      version='3.0',
      description="Switch to the edit skin for certain domains.""",
      long_description=long_description,
      classifiers=[
          "Framework :: Plone",
          "Framework :: Plone :: 4.1",
          "Framework :: Plone :: 4.2",
          "Framework :: Plone :: 4.3",
          "Framework :: Zope2",
          "Programming Language :: Python",
          "Topic :: Software Development :: Libraries :: Python Modules",
          ],
      keywords='',
      author='Maurits van Rees',
      author_email='m.van.rees@zestsoftware.nl',
      url="https://github.com/collective/collective.editskinswitcher",
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
      ],
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
