from setuptools import setup, find_packages

from django_setup import __version__, __author__,__email__,__url__

setup(
    name = 'django-setup',
    version = __version__,
    author = __author__,
    author_email = __email__,
    url = __url__,
    packages = find_packages(exclude=['django_project']),
    include_package_data = True,
    license = 'bsd',
    setup_requires = [ "setuptools_git >= 0.3", ],
    long_description = open('README.txt').read(),
)
