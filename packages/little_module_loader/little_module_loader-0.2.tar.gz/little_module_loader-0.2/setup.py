from setuptools import setup

setup(
    name = "little_module_loader",
    version = "0.2",
    packages = [ 'little_module_loader' ],
    
    author = "Russell Hay",
    author_email = "me@russellhay.com",
    description = "A very simple module loader package for dynamically creating lists of modules, classes, and functions",
    license = "PSF",

    tests_require = [ "nose" ],
    test_suite = "tests",
    url = "http://russellhay.com/tagged/little",
)