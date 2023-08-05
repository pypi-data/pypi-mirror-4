import os
from setuptools import setup, find_packages

def read(filename):
    return open(os.path.join(os.path.join(os.path.dirname(__file__), filename))).read()

setup(name="zkaffold",
      version='0.0.11',
      description="Build out demonstration content for plone",
      long_description=read('README.rst'),
      author="Pat Smith",
      author_email="pat.smith@isotoma.com",
      url="http://pypi.python.org/pypi/zkaffold",
      packages=find_packages(),
      package_data={
          '': ['*.zcml', '*.xml'],
          'zkaffold': [
              'latinwords',
              'exportimport/tests/isotoma_logo.gif',
              'profiles/default/*'],
          },
      include_package_data=True,
      install_requires=[
          'z3c.autoinclude',
          'lxml',
          'DateTime',
          ],
      extras_require={
          'test': ['mock', 'Products.PloneTestCase', 'Plone'],
          },
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
    )
