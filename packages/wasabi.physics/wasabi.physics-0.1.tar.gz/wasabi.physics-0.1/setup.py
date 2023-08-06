from setuptools import setup, find_packages


setup(
    name='wasabi.physics',
    version='0.1',
    description="Pure python 2D physics engine",
    long_description=open('README.rst').read(),
    author='Daniel Pope',
    author_email='mauve@mauveweb.co.uk',
    url='https://bitbucket.org/lordmauve/wasabi-physics',
    packages=find_packages(),
    namespace_packages=['wasabi'],
    install_requires=[
        'wasabi.geom>=0.1',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2 :: Only',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
