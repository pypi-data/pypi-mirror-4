from setuptools import find_packages

from distutils.core import setup


version = '1.0.3'

setup(
    name = "django-daddy-avatar",
    version = version,
    author = "vahid chakoshy",
    author_email = "vchakoshy@gmail.com",
    description = "very simple avatar from gravatar",
    url = "https://github.com/karoon/django-daddy-avatar",
    packages=find_packages(),
    include_package_data = True,
    zip_safe=False,
    classifiers = [
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
        'Natural Language :: Persian',
        
    ]
)
