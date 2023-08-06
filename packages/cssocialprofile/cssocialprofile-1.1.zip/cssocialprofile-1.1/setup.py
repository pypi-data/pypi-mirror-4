from setuptools import setup, find_packages
import sys, os

version = '1.1'

setup(name='cssocialprofile',
      version=version,
      description="SocialProfile app extension",
      long_description=open("README.rst").read(),
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Josu Azpillaga',
      author_email='jazpillaga@codesyntax.com',
      url='http://www.codesyntax.com',
      license='GPL',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
          'django-social-auth',
          'django-registration',
          'tweepy',
          'pyfacebook'
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
