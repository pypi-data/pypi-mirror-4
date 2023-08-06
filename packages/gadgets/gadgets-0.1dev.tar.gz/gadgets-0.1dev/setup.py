from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='gadgets',
      version=version,
      description="A physical computing framework'",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='beaglebone physical computing',
      author='Craig Swank',
      author_email='craigswank@gmail.com',
      url='',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
          'pyzmq',
          'mmap',
      ],
      entry_points="""
      # -*- Entry points: -*-
      [console_scripts]
      enable-pwm=gadgets.utils.enable_pwm:main
      gadgets=gadgets.ui.ui:main
      """,
      )
