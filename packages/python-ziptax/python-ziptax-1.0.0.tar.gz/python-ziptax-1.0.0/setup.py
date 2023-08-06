import os

from setuptools import setup, find_packages
from ziptax import VERSION

README = open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'README.rst')).read()


requires = [
]

setup(
      name='python-ziptax',
      version=VERSION,
      description='Library for zip-tax.com API service',
      long_description=README,
      author='X Studios Inc.',
      author_email='nwhiting@xstudiosinc.com',
      url='https://github.com/xstudios/python-ziptax',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
)