import distribute_setup
distribute_setup.use_setuptools()
from setuptools import setup, find_packages

setup(name="TwitterFollowersGraph",  
      version="1.0",  
      scripts=["followers.py"],  
      py_modules=["auth"],
      install_requires = ['tweepy'],
      packages = find_packages(),
) 

# metadata for upload to PyPI
author = "Alberto Lumbreras",
author_email="alberto.lumbreras@gmail.com",
description="Generates a graph of a user's followers",
license = "GPL",
keywords = "hello world example examples",
url="https://bitbucket.org/alumbreras/twitter-followers-graph",
