from setuptools import setup, find_packages
import os

version = '1.2.1'

setup(name='collective.ptg.allnewest',
      version=version,
      description="Installs all and the newest truegalleries",
      long_description=open("README.rst").read(),
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='plonetruegaller gallery plone addon',
      author='Espen Moe-Nilssen',
      author_email='espen@medialog.no',
      url='https://github.com/collective/collective.ptg.allnewest',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'collective.plonetruegallery >= 3.2a1',
          'collective.ptg.carousel  == 0.2.2',
          'collective.ptg.contactsheet == 1.1.2',
          'collective.ptg.contentflow == 1.0.3',
          'collective.ptg.easyslider == 0.5.1',
          'collective.ptg.fancybox == 1.0.3',
          'collective.ptg.galleria  ==  1.2',
          'collective.ptg.galleriffic == 1.1',
          'collective.ptg.garagedoor == 0.1',
          'collective.ptg.highslide == 1.1.1',
          'collective.ptg.nivogallery == 1.1',
          'collective.ptg.nivoslider == 1.0.6',
          'collective.ptg.pikachoose == 1.0.4',
          'collective.ptg.presentation  == 1.1',
          'collective.ptg.quicksand  == 0.1',
          'collective.ptg.s3slider  == 1.1',
          'collective.ptg.scrollable == 0.3',
          'collective.ptg.sheetgallery == 1.2',
          'collective.ptg.simplegallery == 0.5.4',
          'collective.ptg.supersized == 1.0.4',
          'collective.ptg.thumbnailzoom  == 1.0.5.1',
          'collective.ptg.uigallery == 0.1.1',
          'collective.ptg.quicksand',
          'setuptools',
      ],
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
