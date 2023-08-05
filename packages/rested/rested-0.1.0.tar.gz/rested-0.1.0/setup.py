from distutils.core import setup

VERSION = '0.1.0'

setup(
    name='rested',
    version=VERSION,
    description="A CLI generator",
    long_description="""
    A toolkit that makes it easy to write consistent and usable CLI tools.
    """,
    author='John-John Tedro',
    author_email='johnjohn.tedro@gmail.com',
    url='http://github.com/udoprog/rested',
    license='GPLv3',
    packages=[
        'rested',
        'rested.ext',
        'rested.broker',
    ],
    classifiers=[
        "Topic :: Software Development :: User Interfaces"
    ]
)
