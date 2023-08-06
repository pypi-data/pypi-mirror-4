from setuptools import setup, find_packages
import os

version = '0.1'

setup(name='cmsplugin-fb-agenda',
      version=version,
      description="django-cms plugin: display the agenda of a facebook user",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.rst")).read(),
      # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
          "Programming Language :: Python",
          "Topic :: Software Development :: Libraries :: Python Modules",
      ],
      author='GISA Elkartea',
      author_email='kontaktua@gisa-elkartea.org',
      url='http://lagunak.gisa-elkartea.org/projects/cmplugin-fb-agenda',
      license='GPL',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
          'django-cms',
          'facebook-sdk',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
