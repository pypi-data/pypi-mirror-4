from setuptools import setup, find_packages
import sys, os

version = '1.0'

setup(name='renren',
      version=version,
      description="renren python sdk",
      long_description="""\
renren sdk""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='renren sdk',
      author='lanjinmin',
      author_email='463473243@qq.com',
      url='http://yaofan.9miao.com/other/1',
      license='',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
