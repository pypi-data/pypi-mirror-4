#   One day, this file will setup the xsanio_server package
from setuptools import setup, find_packages


setup(
    name = 'xsanio-server',
    version = '0.3.1',
    packages = find_packages(),
    author = 'Vasily Kolosov',
    author_email = 'vasily.kolosov@shortcut.ru',
    include_package_data = True,
    zip_safe=False,
)
