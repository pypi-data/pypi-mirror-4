from setuptools import find_packages
from setuptools import setup

version = '0.1-1'

setup(
    name='bobtemplates.fanstatic',
    version=version,
    description="mr.bob template for Fanstatic packages",
    long_description=open("README.rst").read() + "\n" +
                     open("CHANGES.rst").read(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Utilities",
    ],
    keywords='',
    author='Nuno Teixeira',
    author_email='teixas@gmail.com',
    url='https://github.com/teixas/bobtemplates.fanstatic',
    license='BSD',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['bobtemplates'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'mr.bob',
    ],
    entry_points={},
)
