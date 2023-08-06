from setuptools import setup

from wysiweb import __VERSION__

setup(
    name='wysiweb',
    version=__VERSION__,
    url='http://jspi.es/wysiweb',
    license='LICENSE',
    author='Jeffrey R. Spies',
    author_email='jspies@gmail.com',
    description='File-system based router and static website generator',
    long_description=open('README.md').read(),
    packages=['wysiweb'],
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    classifiers=[
        "Development Status :: 4 - Beta",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "License :: OSI Approved :: Apache Software License",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ]
)