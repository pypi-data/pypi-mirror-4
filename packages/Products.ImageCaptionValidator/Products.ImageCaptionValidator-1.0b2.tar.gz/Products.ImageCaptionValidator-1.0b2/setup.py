from setuptools import setup, find_packages
import os

version = '1.0b2'

setup(name='Products.ImageCaptionValidator',
      version=version,
      description="Validator that checks imageCaption is set, if an image has been added either directly or via a reference",
      long_description=open(os.path.join("Products", "ImageCaptionValidator", "readme.txt")).read() + '\n\n' +\
          open(os.path.join("Products", "ImageCaptionValidator", "changes.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Zope2",
        "Framework :: Plone",
        ],
      keywords='python plone archetypes validation',
      author='Nidelven IT',
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
