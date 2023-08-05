from setuptools import setup, find_packages
import os

version = '1.0.6'

setup(name='Products.NewsPage',
      version=version,
      description="A content type that displays recent news and lets users pin the 3 first stories.",
      long_description=open(os.path.join("Products", "NewsPage", "readme.txt")).read() + '\n\n' + 
                       open(os.path.join("Products", "NewsPage", "changes.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Plone",
        ],
      keywords='python plone archetypes contenttype presentation',
      author='Morten W. Petersen',
      author_email='info@nidelven-it.no',
      url='http://www.nidelven-it.no/d',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
