import distribute_setup
distribute_setup.use_setuptools()

from setuptools import setup, find_packages

setup(
      name='webveripy',
      version='0.3',
      packages=find_packages(),
      py_modules=["distribute_setup"],
      install_requires = ["httplib2>=0.7.6"],
    
      author="john haren",
      author_email="john.haren@gmail.com",
      url="https://github.com/jharen/Webveripy",
      description="All-purpose web verification framework."
      
)
