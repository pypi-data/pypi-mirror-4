from setuptools import setup, find_packages

version = '1.0.3'

setup(name='collective.sortmyfolder',
      version=version,
      description=("Reveal some not-so-hidden Plone feature for sorting "
                   "your folders"),
      long_description=(open("README.txt").read().strip() + "\n\n" +
                        open("CHANGES.rst").read().strip()),
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
          "Framework :: Plone",
          "Programming Language :: Python",
          "Development Status :: 5 - Production/Stable",
          ],
      keywords='plone folder sort',
      author='RedTurtle Technology',
      author_email='sviluppoplone@redturtle.net',
      url='https://github.com/collective/collective.sortmyfolder',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
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
