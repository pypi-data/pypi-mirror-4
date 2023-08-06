import os
from setuptools import setup

# Utility function to read the README file.  
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "piui",
    version = "0.0.1",
    author = "David Singleton",
    author_email = "davidsingleton@gmail.com",
    description = ("Add a mobile UI to your RaspberryPi"
                   " project."),
    license = "BSD",
    keywords = "raspberrypi mobile ui",
    url = "http://github.com/dps/piui",
    packages=['piui'],
    long_description=read('README.md'),
    package_data = {'piui' : ['piui/static/*']},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: BSD License",
    ],
)
