import os
from setuptools import setup
from pyavdesk import VERSION

f = open(os.path.join(os.path.dirname(__file__), 'README'))
readme = f.read()
f.close()

setup(
    name='pyavdesk',
    version='.'.join(map(str, VERSION)),
    description='pyavdesk is a Python wrapper for dwavdapi C library to manipulate Dr.Web AV-Desk server resources.',
    long_description=readme,
    author='Doctor Web, Ltd.',
    author_email='support@drweb.com',
    url='http://www.drweb.com',
    packages=['pyavdesk'],
    include_package_data=True,
    install_requires=['setuptools'],
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Other Environment',
        'Intended Audience :: Developers',
        'License :: Other/Proprietary License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
    ],
)