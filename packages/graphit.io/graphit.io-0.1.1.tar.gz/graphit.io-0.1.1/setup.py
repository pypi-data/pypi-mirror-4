
from distribute_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages

setup(
      name = "graphit.io",
      version = "0.1.1",
      packages = find_packages(),
      install_requires=['distribute>=0.6.35', 'requests>=1.1.0'],
      author = "Eric Seifert",
      author_email = "seiferteric@gmail.com",
      description = "Graphit.io Graphing API library",
      keywords = "graphit graph Graphit.io", 
      url = "https://graphit.io/",
      zip_safe = True,
      entry_points = {
        'console_scripts': [
          'graphit = graphit.cli:main'
        ]
      }
)
