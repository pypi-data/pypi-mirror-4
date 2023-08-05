from setuptools import setup, find_packages
import os

version = "3.1"

setup(name='collective.plonetruegallery',
      version=version,
      description="A gallery/slideshow product for plone that can aggregate "
                  "from picasa and flickr or use plone images.",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Framework :: Plone :: 3.3",
        "Framework :: Plone :: 4.0",
        "Framework :: Plone :: 4.1",
        "Framework :: Plone :: 4.2"
        ],
      keywords='gallery plone slideshow photo photos image images picasa '
               'flickr highslide nivoslider nivogallery pikachoose fancybox '
               'galleriffic galleria',
      author='Nathan Van Gheem',
      author_email='vangheem@gmail.com',
      url='http://www.plone.org/products/plone-true-gallery',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'plone.app.z3cform',
          'collective.ptg.galleria'
      ],
      extras_require=dict(
          tests=[
            'flickrapi',
            'gdata',
          ],
          flickr=['flickrapi'],
          picasa=['gdata'],
          all=['flickrapi', 'gdata']
      ),
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """
)
