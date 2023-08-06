from setuptools import find_packages

from distutils.core import setup


version = '1.0.1'

setup(
    name = "django-daddy-avatar",
    version = version,
    author = "vahid chakoshy",
    author_email = "vchakoshy@gmail.com",
    description = "daddy avatar for pinterest apllication like in Django",
    url = "http://www.wisgoon.com/",
    packages=find_packages(),
    include_package_data = True,
    zip_safe=False,
)
