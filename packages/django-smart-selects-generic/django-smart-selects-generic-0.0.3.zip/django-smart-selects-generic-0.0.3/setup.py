import os
from setuptools import setup, find_packages

from smart_generic import VERSION

setup(name="django-smart-selects-generic",
      version=VERSION,
      description="Django application to handle chained generic model fields.",
      long_description=file(
          os.path.join(
              os.path.dirname(__file__),
              'README.md'
          )
      ).read(),
      author="Victor Safronovich",
      author_email="vsafronovich@gmail.com",
      url='http://bitbucket.org/suvitorg/django-smart-selects-generic',
      packages=find_packages(),
      install_requires=['django-smart-selects>=1.0.5,<2.0'],
      include_package_data=True,
)
         
