from setuptools import find_packages

from distutils.core import setup

version = '1.0.3'

setup(
    name = "django-user-profile",
    version = version,
    packages = ['user_profile'],
    author = "vahid chakoshy",
    author_email = "vchakoshy@gmail.com",
    description = "user profile for pinterest apllication like in Django",
    url = "http://www.wisgoon.com/",
    py_modules = ["user_rofile"],
    #package_dir = {},
    package_dir = {'user_rofile': 'user_rofile'},
    include_package_data = True,
    zip_safe=False,
)
