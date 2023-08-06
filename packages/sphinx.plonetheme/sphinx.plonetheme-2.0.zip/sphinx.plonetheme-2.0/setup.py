from setuptools import setup, find_packages

version = '2.0'

setup(name='sphinx.plonetheme',
      version=version,
      description="Addon for Plone",
      long_description=open("README.rst").read() + "\n" +
                       open("CHANGES.txt").read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
      ],
      keywords='sphinx theme',
      author='Gilles Lenfant',
      author_email='gilles.lenfant@alterway.fr',
      url='https://github.com/collective/sphinx.plonetheme',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['sphinx'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'sphinxjp.themecore',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      [sphinx_themes]
      path = sphinx.plonetheme:get_path
      """,
      )
