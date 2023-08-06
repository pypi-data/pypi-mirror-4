from setuptools import setup

import greenrocket

setup(
    name='GreenRocket',
    version=greenrocket.__version__,
    description="A simple implementation of Observer pattern via Signals",
    long_description=greenrocket.__doc__,
    classifiers=[
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords='',
    author='Dmitry Vakhrushev',
    author_email='self@kr41.net',
    url='https://bitbucket.org/kr41/greenrocket',
    download_url='https://bitbucket.org/kr41/greenrocket/downloads',
    license='BSD',
    packages=['greenrocket'],
    include_package_data=True,
    zip_safe=True,
)
