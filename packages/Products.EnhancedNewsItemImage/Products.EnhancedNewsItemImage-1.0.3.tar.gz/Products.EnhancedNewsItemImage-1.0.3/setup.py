from setuptools import setup, find_packages
import os

version = '1.0.3'

setup(name='Products.EnhancedNewsItemImage',
      version=version,
      description="Enhances regular news items so they can reference an image and makes image caption a requirement if image is set.",
      long_description=open(os.path.join("Products", "EnhancedNewsItemImage", "readme.txt")).read() + '\n\n' +\
          open(os.path.join("Products", "EnhancedNewsItemImage", "changes.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Zope2",
        "Framework :: Plone",
        ],
      keywords='python plone atcontenttypes archetypes monkeypatch news accessibility',
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
          "Products.ImageCaptionValidator>=1.0b",
          "Products.PatchPloneContent>=1.0.2",
          "archetypes.referencebrowserwidget",
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
