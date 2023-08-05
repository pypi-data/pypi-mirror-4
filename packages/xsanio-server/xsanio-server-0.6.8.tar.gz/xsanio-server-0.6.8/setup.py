#   One day, this file will setup the xsanio_server package
from setuptools import setup, find_packages
import sys
import os


new_version = ''
#   Read the version and increment it
version_file_path = 'VERSION'
if os.path.isfile(version_file_path):
    version_file = open(version_file_path, 'r')
    current_version = version_file.readline()
    version_file.close()

    version_numbers = current_version.split('.')
    version_numbers = [int(x) for x in version_numbers]

    if sys.argv == ['setup.py', 'sdist']:
        version_numbers[2] += 1
        for n in reversed(range(1, 3)):
            if version_numbers[n] >= 10:
                version_numbers[n] = 0
                version_numbers[n-1] += 1

    version_numbers = [str(x) for x in version_numbers]

    new_version = '.'.join(version_numbers)
    print "New version is %s" % new_version

    #   Save it in the file
    version_file = open(version_file_path, 'w')
    version_file.write(new_version)
    version_file.close()

setup(
    name = 'xsanio-server',
    version = new_version,
    packages = find_packages(),
    author = 'Vasily Kolosov',
    author_email = 'vasily.kolosov@shortcut.ru',
    include_package_data = True,
    zip_safe=False,
    install_requires=[
        'django',
    ],
    description='Mac OS X Server Xsan I/O load monitoring tool'
)
