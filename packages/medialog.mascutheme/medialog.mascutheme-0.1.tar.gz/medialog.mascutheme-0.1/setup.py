from setuptools import setup, find_packages
import os

version = '0.1'

setup(name='medialog.mascutheme',
      version=version,
      description="Medialog Mascutheme",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='Plone Theme Mascutheme',
      author='EMN',
      author_email='espen@medialog.no',
      url='http://github.com/espenmn/medialog.mascutheme',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['medialog'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'plonetheme.classic',
          'wildcard.foldercontents',
          'medialog.portlet.placeholder',
          'collective.responsivetheme',
          'medialog.qrcode',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      setup_requires=["PasteScript"],
      paster_plugins=["ZopeSkel"],
      )
