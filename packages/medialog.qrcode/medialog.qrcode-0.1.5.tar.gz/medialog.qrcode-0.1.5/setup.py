from setuptools import setup, find_packages
import os

version = '0.1.5'

setup(name='medialog.qrcode',
      version=version,
      description="QRcode views and portlet for Plone.",
      long_description=open("README.txt").read(),
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='QRcode QR generator ',
      author='Espen Moe-Nilssen',
      author_email='espen@medialog.no',
      url='https://github.com/espenmn/medialog.qrcode/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['medialog'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'qrcode',
      ],
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      setup_requires=["PasteScript"],
      paster_plugins=["ZopeSkel"],
      )
